# app.py
# Bond Present Value Calculator built with Streamlit

# -----------------------------
# 1. Import libraries
# -----------------------------
import streamlit as st   # Builds the web app
import pandas as pd      # Builds the cash flow table


# -----------------------------
# 2. Page setup
# -----------------------------
st.set_page_config(
    page_title="Bond PV Calculator",
    page_icon="💵",
    layout="centered"
)

st.title("💵 Bond Present Value Calculator")
st.write("Enter the bond's details below to calculate its present value (fair price today).")


# -----------------------------
# 3. User inputs
# -----------------------------
st.header("Bond Inputs")

# Split the inputs into two side-by-side columns for a cleaner look
col1, col2 = st.columns(2)

with col1:
    # Face value: the amount repaid when the bond matures
    face_value = st.number_input(
        "Face Value (FV) $",
        min_value=0.0, value=1000.0, step=100.0
    )

    # Annual coupon payment: total interest the bond pays per year
    annual_pmt = st.number_input(
        "Annual Coupon Payment (PMT) $",
        min_value=0.0, value=50.0, step=5.0
    )

with col2:
    # Market rate (yield): the return investors require, entered as a percent
    rate_percent = st.number_input(
        "Market Rate / Yield (%)",
        min_value=0.0, value=6.0, step=0.25
    )

    # Time to maturity in whole years
    years = st.number_input(
        "Time to Maturity (years)",
        min_value=1, value=10, step=1
    )

# How often the bond pays coupons each year
frequency_label = st.selectbox(
    "Coupon Payments per Year",
    ["Annual (1)", "Semiannual (2)", "Quarterly (4)", "Monthly (12)"]
)

# Turn the dropdown text into a number
frequency_map = {
    "Annual (1)": 1,
    "Semiannual (2)": 2,
    "Quarterly (4)": 4,
    "Monthly (12)": 12
}
freq = frequency_map[frequency_label]


# -----------------------------
# 4. Convert yearly inputs into per-period values
# -----------------------------
r = (rate_percent / 100) / freq      # Rate per period (e.g., 6% semiannual -> 0.03)
n = int(years * freq)                # Total number of periods
pmt = annual_pmt / freq              # Coupon payment per period


# -----------------------------
# 5. The present value function
# -----------------------------
def bond_present_value(face_value, pmt, r, n):
    """Returns the PV of the coupons and the PV of the face value."""
    if r == 0:
        # Special case: with a 0% rate, nothing is discounted
        pv_coupons = pmt * n
        pv_face = face_value
    else:
        # PV of all coupon payments (annuity formula)
        pv_coupons = pmt * (1 - (1 + r) ** -n) / r
        # PV of the face value received at maturity
        pv_face = face_value / (1 + r) ** n
    return pv_coupons, pv_face


pv_coupons, pv_face = bond_present_value(face_value, pmt, r, n)
bond_price = pv_coupons + pv_face


# -----------------------------
# 6. Display the results
# -----------------------------
st.divider()
st.header("Results")

# The main answer in a big, easy-to-read format
st.metric("Present Value of Bond", f"${bond_price:,.2f}")

# Show where the value comes from
col3, col4 = st.columns(2)
col3.metric("PV of Coupon Payments", f"${pv_coupons:,.2f}")
col4.metric("PV of Face Value", f"${pv_face:,.2f}")

# Say whether the bond trades at a premium, discount, or par
if abs(bond_price - face_value) < 0.01:
    st.info("This bond is priced **at par** (price = face value).")
elif bond_price > face_value:
    st.success("This bond is priced at a **premium** (price > face value) "
               "because its coupon rate is higher than the market rate.")
else:
    st.warning("This bond is priced at a **discount** (price < face value) "
               "because its coupon rate is lower than the market rate.")


# -----------------------------
# 7. Show the formula used
# -----------------------------
st.subheader("Formula Used")
st.latex(r"PV = PMT \times \frac{1 - (1 + r)^{-n}}{r} + \frac{FV}{(1 + r)^{n}}")
st.write(
    f"Here: PMT = ${pmt:,.2f} per period, r = {r:.4%} per period, "
    f"n = {n} periods, FV = ${face_value:,.2f}"
)


# -----------------------------
# 8. Optional cash flow table
# -----------------------------
with st.expander("See period-by-period cash flows"):
    rows = []
    for period in range(1, n + 1):
        # The final period pays the last coupon plus the face value
        cash_flow = pmt + face_value if period == n else pmt
        discount_factor = 1 / (1 + r) ** period
        rows.append({
            "Period": period,
            "Cash Flow ($)": round(cash_flow, 2),
            "Discount Factor": round(discount_factor, 6),
            "Present Value ($)": round(cash_flow * discount_factor, 2)
        })

    table = pd.DataFrame(rows)
    st.dataframe(table, hide_index=)
