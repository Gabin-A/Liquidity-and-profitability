import math
anchors_df = default_anchors()


st.title("📈 Economies-of-Scale Growth Simulator")
st.caption("Self-financed growth with reinvestment, using piecewise-linear per-unit margin vs. fleet size.")


st.subheader("Anchors (edit if needed)")
anchors_df = st.data_editor(
anchors_df,
num_rows="dynamic",
hide_index=True,
use_container_width=True,
column_config={
"Units_Anchor": st.column_config.NumberColumn(step=1, help="Fleet size at which this margin applies."),
"PerUnitMargin": st.column_config.NumberColumn(format="$%.0f", help="Per-unit margin at that fleet size (per month)."),
},
)


# ---------------------- RUN SIM ------------------------
try:
    params = SimParams(
        unit_cost=float(unit_cost),
        starting_cash=float(starting_cash),
        overhead_per_month=float(overhead),
        horizon_months=int(horizon),
        max_new_units_per_month=max_builds_opt,
        hold_flat_above_max=bool(hold_flat),
        lead_time_months=int(lead_time),
    )

    result = simulate(params, anchors_df)

    # -------------------- LAYOUT -----------------------
    m1, m2, m3, m4 = st.columns(4)
    last = result.monthly.iloc[-1]
    m1.metric("Final Units", f"{int(last['Units_End']):,}")
    m2.metric("Final Monthly Profit", f"${last['MonthlyProfit']:,.0f}")
    m3.metric("Ending Cash", f"${last['Cash_End']:,.0f}")
    m4.metric("Per-Unit Margin (end)", f"${last['PerUnitMargin']:,.0f}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Units & Profit over time")
        plot_df = result.monthly[["Month", "Units_Start", "MonthlyProfit"]].copy()
        st.line_chart(plot_df.set_index("Month"))
    with c2:
        st.subheader("Cash position over time")
        st.line_chart(result.monthly.set_index("Month")["Cash_Start"])

    st.subheader("Milestones")
    st.dataframe(result.milestones, use_container_width=True, hide_index=True)

    st.subheader("Detailed timeline")
    st.dataframe(result.monthly, use_container_width=True)

    # Downloads
    st.download_button(
        label="Download timeline CSV",
        data=result.monthly.to_csv(index=False).encode("utf-8"),
        file_name="growth_simulation_timeline.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download anchors CSV",
        data=normalize_anchors(anchors_df).to_csv(index=False).encode("utf-8"),
        file_name="anchors.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Error: {e}")
    st.exception(e)
