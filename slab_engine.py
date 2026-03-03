from database import get_connection

# -----------------------
# Save Slabs
# -----------------------
def save_slabs(user_id, slabs):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM slab_config WHERE user_id = ?", (user_id,))

    for slab in slabs:
        cursor.execute(
            "INSERT INTO slab_config (user_id, min_units, max_units, rate_per_unit) VALUES (?, ?, ?, ?)",
            (user_id, slab["min"], slab["max"], slab["rate"])
        )

    conn.commit()
    conn.close()


# -----------------------
# Save Billing Settings
# -----------------------
def save_billing_settings(user_id, fixed_charge, load, surcharge):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO billing_settings 
        (user_id, fixed_charge_per_kw, sanctioned_load, surcharge_percent)
        VALUES (?, ?, ?, ?)
    """, (user_id, fixed_charge, load, surcharge))

    conn.commit()
    conn.close()

def get_slabs(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT min_units, max_units, rate_per_unit
        FROM slab_config
        WHERE user_id = ?
        ORDER BY min_units ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_billing_settings(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fixed_charge_per_kw, sanctioned_load, surcharge_percent
        FROM billing_settings
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return row


# -----------------------
# Check If Bill Exists
# -----------------------
def bill_exists(user_id, month, year):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM bills
        WHERE user_id = ? AND month = ? AND year = ?
    """, (user_id, month, year))

    result = cursor.fetchone()
    conn.close()

    return result is not None


# -----------------------
# Insert / Replace Bill
# -----------------------
def save_bill(user_id, bill_data, replace=False):
    conn = get_connection()
    cursor = conn.cursor()

    if replace:
        cursor.execute("""
            DELETE FROM bills
            WHERE user_id = ? AND month = ? AND year = ?
        """, (user_id, bill_data["month"], bill_data["year"]))

    cursor.execute("""
        INSERT INTO bills (
            user_id, month, year,
            units_consumed,
            energy_charges,
            fixed_charges,
            ed_surcharge,
            total_grid_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        bill_data["month"],
        bill_data["year"],
        bill_data.get("units_consumed"),
        bill_data.get("energy_charges"),
        bill_data.get("fixed_charges"),
        bill_data.get("ed_surcharge"),
        bill_data.get("total_grid_amount")
    ))

    conn.commit()
    conn.close()

def get_all_bills(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT month, year,
               units_consumed,
               energy_charges,
               fixed_charges,
               ed_surcharge,
               total_grid_amount
        FROM bills
        WHERE user_id = ?
        ORDER BY year ASC, month ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def calculate_bill(units, slabs, fixed_charge, sanctioned_load, surcharge_percent):

    remaining_units = units
    energy_cost = 0

    for slab in slabs:
        slab_min = slab["min"]
        slab_max = slab["max"]
        rate = slab["rate"]

        if remaining_units <= 0:
            break

        slab_range = slab_max - slab_min + 1
        slab_units = min(remaining_units, slab_range)

        energy_cost += slab_units * rate
        remaining_units -= slab_units

    fixed_cost = fixed_charge * sanctioned_load

    surcharge = (energy_cost + fixed_cost) * (surcharge_percent / 100)

    total = energy_cost + fixed_cost + surcharge

    return round(total, 2)