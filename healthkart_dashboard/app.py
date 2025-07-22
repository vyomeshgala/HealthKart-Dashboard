import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="HealthKart Influencer Dashboard", layout="wide")
st.markdown("## HealthKart Influencer Campaign Performance Tracker")
st.markdown("Track ROI, analyze influencer performance, and get actionable insights for your marketing campaigns.")

# ===========================
# 🔽 Load & Clean Data Early
# ===========================
@st.cache_data
def load_and_clean_data():
    try:
        influencers = pd.read_csv("data/influencers.csv")
        posts = pd.read_csv("data/posts.csv")
        tracking = pd.read_csv("data/tracking_data.csv")
        payouts = pd.read_csv("data/payouts.csv")

        # Standardize column names: strip whitespace and lowercase
        for df in [influencers, posts, tracking, payouts]:
            df.columns = df.columns.str.strip().str.lower()

        return influencers, posts, tracking, payouts
    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

try:
    influencers, posts, tracking, payouts = load_and_clean_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# ===========================
# 🔍 Enhanced Sidebar Filters
# ===========================
st.sidebar.header("🔍 Advanced Filters")

# Validate required columns for basic functionality
required_columns = {
    'influencers': ['platform'],
    'tracking': ['campaign']
}
missing_columns = []
for df_name, cols in required_columns.items():
    df = locals()[df_name]
    missing = [col for col in cols if col not in df.columns]
    missing_columns.extend([f"{col} in {df_name}" for col in missing])

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# 1. Platform Filter
selected_platform = st.sidebar.multiselect(
    "🎯 Platform",
    options=influencers["platform"].unique(),
    default=influencers["platform"].unique(),
    help="Select social media platforms to analyze"
)

# 2. Campaign Filter
selected_campaign = st.sidebar.multiselect(
    "📢 Campaign",
    options=tracking["campaign"].unique(),
    default=tracking["campaign"].unique(),
    help="Choose specific marketing campaigns"
)

# 3. Product Filter (using 'product' from tracking_data)
if 'product' in tracking.columns:
    selected_product = st.sidebar.multiselect(
        "🛍️ Product",
        options=tracking["product"].unique(),
        default=tracking["product"].unique(),
        help="Filter by specific products"
    )
    product_col = 'product'
else:
    selected_product = None
    st.sidebar.info("ℹ️ Product filtering unavailable - 'product' column not found")

# 4. Influencer Type Filter (using 'category' from influencers)
if 'category' in influencers.columns:
    selected_influencer_type = st.sidebar.multiselect(
        "👤 Influencer Category",
        options=influencers["category"].unique(),
        default=influencers["category"].unique(),
        help="Filter by influencer categories (fitness, nutrition, etc.)"
    )
    influencer_type_col = 'category'
else:
    selected_influencer_type = None
    influencer_type_col = None
    st.sidebar.info("ℹ️ Category filtering unavailable")

# Follower Count Filter (using 'follower count' from influencers)
follower_col = None
if 'follower count' in influencers.columns:
    follower_col = 'follower count'
elif 'follower_count' in influencers.columns:
    follower_col = 'follower_count'
elif 'followers' in influencers.columns:
    follower_col = 'followers'

if follower_col:
    # Convert to numeric and handle errors
    influencers[follower_col] = pd.to_numeric(influencers[follower_col], errors='coerce')
    min_followers = int(influencers[follower_col].min()) if not influencers[follower_col].isna().all() else 0
    max_followers = int(influencers[follower_col].max()) if not influencers[follower_col].isna().all() else 1000000

    selected_follower_range = st.sidebar.slider(
        "👥 Follower Count Range",
        min_value=min_followers,
        max_value=max_followers,
        value=(min_followers, max_followers),
        help="Filter influencers by follower count"
    )
else:
    selected_follower_range = None
    st.sidebar.info("ℹ️ Follower filtering unavailable")

# Gender Filter (if available)
if 'gender' in influencers.columns:
    selected_gender = st.sidebar.multiselect(
        "⚧ Gender",
        options=influencers["gender"].unique(),
        default=influencers["gender"].unique(),
        help="Filter by influencer gender"
    )
else:
    selected_gender = None

# Date Range Filter (if date columns exist)
date_columns = ['date', 'post_date', 'campaign_date', 'created_at']
date_col = None
for col in date_columns:
    if col in posts.columns:
        date_col = col
        break

if date_col:
    try:
        posts[date_col] = pd.to_datetime(posts[date_col], errors='coerce')
        min_date = posts[date_col].min().date()
        max_date = posts[date_col].max().date()

        selected_date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter posts by date range"
        )
    except:
        selected_date_range = None
else:
    selected_date_range = None

# Clear Filters Button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

# ===========================
# 🎯 Apply All Filters
# ===========================
st.sidebar.markdown("---")
st.sidebar.markdown("**Active Filters:**")

# Start with base data
filtered_influencers = influencers[influencers["platform"].isin(selected_platform)]
filtered_tracking = tracking[tracking["campaign"].isin(selected_campaign)]

# Apply Product Filter
if selected_product and product_col:
    filtered_tracking = filtered_tracking[filtered_tracking[product_col].isin(selected_product)]
    st.sidebar.text(f"🛍️ Products: {len(selected_product)}")

# Apply Influencer Type Filter
if selected_influencer_type and influencer_type_col:
    filtered_influencers = filtered_influencers[
        filtered_influencers[influencer_type_col].isin(selected_influencer_type)]
    st.sidebar.text(f"👤 Categories: {len(selected_influencer_type)}")

# Apply Follower Range Filter
if selected_follower_range and follower_col:
    filtered_influencers = filtered_influencers[
        (filtered_influencers[follower_col] >= selected_follower_range[0]) &
        (filtered_influencers[follower_col] <= selected_follower_range[1])
        ]
    st.sidebar.text(f"👥 Followers: {selected_follower_range[0]:,} - {selected_follower_range[1]:,}")

# Apply Gender Filter
if selected_gender:
    filtered_influencers = filtered_influencers[filtered_influencers["gender"].isin(selected_gender)]
    st.sidebar.text(f"⚧ Genders: {len(selected_gender)}")

# Show filter summary
st.sidebar.markdown(f"**Results:** {len(filtered_influencers)} influencers, {len(filtered_tracking)} records")

# ===========================
# 🧑‍💼 Influencer Details
# ===========================
st.subheader("🧑‍💼 Influencer Details")

# Show filter summary in main area
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Influencers", len(filtered_influencers))
with col2:
    st.metric("Total Campaigns",
              len(filtered_tracking['campaign'].unique()) if 'campaign' in filtered_tracking.columns else 0)
with col3:
    st.metric("Total Records", len(filtered_tracking))
with col4:
    st.metric("Platforms Selected", len(selected_platform))

# Display filtered influencer data
if not filtered_influencers.empty:
    st.dataframe(filtered_influencers, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ No influencers match the selected filters.")

# ===========================
# 📢 Post Performance
# ===========================
st.subheader("📢 Post Performance")

# Check merge keys
if 'influencer_id' not in posts.columns:
    st.error("'influencer_id' column not found in posts data.")
    st.stop()
if 'id' not in influencers.columns:
    st.error("'id' column not found in influencers data.")
    st.stop()

# Merge posts with filtered influencers
merged_posts = posts.merge(filtered_influencers, left_on='influencer_id', right_on='id', how='inner')

# Handle platform ambiguity after merge
if 'platform_x' in merged_posts.columns and 'platform_y' in merged_posts.columns:
    merged_posts['platform'] = merged_posts['platform_y']  # Prefer influencers' platform
elif 'platform_x' in merged_posts.columns:
    merged_posts['platform'] = merged_posts['platform_x']
elif 'platform' not in merged_posts.columns:
    st.error("No 'platform' column available after merge.")
    st.stop()

# Apply date filter to posts
if selected_date_range and date_col and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    merged_posts = merged_posts[
        (merged_posts[date_col].dt.date >= start_date) &
        (merged_posts[date_col].dt.date <= end_date)
        ]

# Display relevant columns
display_cols = ['influencer_id', 'platform', 'date', 'url', 'caption', 'reach', 'likes', 'comments']
if influencer_type_col:
    display_cols.append(influencer_type_col)
available_cols = [col for col in display_cols if col in merged_posts.columns]

if available_cols and not merged_posts.empty:
    st.dataframe(merged_posts[available_cols], use_container_width=True, hide_index=True)
else:
    st.warning("No post performance data matches the selected filters.")

# ===========================
# 💰 ROAS & Campaign Performance
# ===========================
st.subheader("💰 ROAS & Campaign Performance")

try:
    # Required columns check
    roas_reqs = {
        'tracking': ['influencer_id', 'revenue'],
        'payouts': ['influencer_id', 'total_payout'],
        'influencers': ['id', 'name']
    }
    for src, cols in roas_reqs.items():
        df = locals()[src]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            st.error(f"Missing in {src}: {missing}")
            st.stop()

    # Use filtered tracking data
    revenue_df = filtered_tracking.groupby('influencer_id')['revenue'].sum().reset_index()
    revenue_df.rename(columns={'revenue': 'total_revenue'}, inplace=True)

    # Filter payouts to match filtered influencers
    filtered_influencer_ids = filtered_influencers['id'].tolist()
    filtered_payouts = payouts[payouts['influencer_id'].isin(filtered_influencer_ids)]

    # Merge with payouts and name
    roas_df = filtered_payouts.merge(revenue_df, on='influencer_id', how='left')
    roas_df['total_revenue'] = roas_df['total_revenue'].fillna(0)
    roas_df['roas'] = (roas_df['total_revenue'] / roas_df['total_payout']).round(2)
    roas_df = roas_df.merge(filtered_influencers[['id', 'name']], left_on='influencer_id', right_on='id', how='left')

    # Show ROAS table
    roas_display_cols = ['name', 'basis', 'rate', 'orders', 'total_payout', 'total_revenue', 'roas']
    if influencer_type_col:
        roas_display_cols.append(influencer_type_col)
    final_display_cols = [col for col in roas_display_cols if col in roas_df.columns]

    if final_display_cols and not roas_df.empty:
        st.dataframe(roas_df[final_display_cols], use_container_width=True, hide_index=True)

        # ROAS Chart
        st.subheader("📊 ROAS Comparison Chart")
        chart_data = roas_df[['name', 'roas']].dropna().sort_values('roas', ascending=False)
        if not chart_data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.barh(chart_data['name'], chart_data['roas'], color='teal')
            ax.set_xlabel("ROAS")
            ax.set_ylabel("Influencer")
            ax.set_title("ROAS by Influencer (Filtered Results)")

            # Add value labels on bars
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                ha='left', va='center', fontweight='bold')

            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.warning("No ROAS data matches the selected filters.")

except Exception as e:
    st.error(f"Error calculating ROAS: {e}")
    st.write("Please verify your data structure.")

# ===========================
# 💰 ROI & Campaign Performance
# ===========================
st.subheader("📈 ROI & Campaign Performance")

# Ensure total_payout exists
payouts_roi = payouts.copy()
if 'payout_amount' in payouts_roi.columns:
    payouts_roi.rename(columns={'payout_amount': 'total_payout'}, inplace=True)
elif 'total_payout' not in payouts_roi.columns:
    st.error("❌ 'total_payout' or 'payout_amount' missing in payouts data.")
    st.stop()

# Merge filtered tracking and payouts
roi_df = pd.merge(filtered_tracking, payouts_roi, on='influencer_id', how='inner')
roi_df['revenue'] = pd.to_numeric(roi_df['revenue'], errors='coerce').fillna(0)
roi_df['total_payout'] = pd.to_numeric(roi_df['total_payout'], errors='coerce').fillna(0)

# Calculate ROI
roi_df['roi (%)'] = roi_df.apply(
    lambda row: ((row['revenue'] - row['total_payout']) / row['total_payout']) * 100
    if row['total_payout'] != 0 else 0,
    axis=1
)
roi_df['roi (%)'] = roi_df['roi (%)'].round(2)

# Display
if not roi_df.empty:
    display_roi_cols = ['influencer_id', 'revenue', 'total_payout', 'roi (%)']
    if 'campaign' in roi_df.columns:
        display_roi_cols.insert(1, 'campaign')
    if selected_product and product_col:
        display_roi_cols.insert(-1, product_col)

    st.dataframe(
        roi_df[display_roi_cols],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("No ROI data matches the selected filters.")

# 📊 Incremental ROAS - FINAL VERSION (Supports Required Schema)
st.subheader("📊 Incremental ROAS")
try:
    # --- Step 1: Clean column names early ---
    tracking_clean = filtered_tracking.copy()
    tracking_clean.columns = tracking_clean.columns.str.strip().str.lower()

    payouts_clean = payouts_roi.copy()
    payouts_clean.columns = payouts_clean.columns.str.strip().str.lower()

    # --- Step 2: Validate required columns ---
    required_tracking = ['influencer_id', 'revenue', 'orders']
    missing_in_tracking = [col for col in required_tracking if col not in tracking_clean.columns]

    if missing_in_tracking:
        st.warning(f"⚠️ Missing required columns in tracking data: {', '.join(missing_in_tracking)}")
        st.info("Available tracking columns: " + ", ".join(tracking_clean.columns.tolist()))
    else:
        # --- Step 3: Merge with suffixes to handle duplicate 'orders' ---
        merged_df = pd.merge(
            tracking_clean,
            payouts_clean,
            on='influencer_id',
            how='inner',
            suffixes=('_tracking', '_payouts')  # Explicitly name conflicts
        )

        # --- Step 4: Resolve column names ---
        # Use 'orders_tracking' as the real customer orders (from tracking)
        # Rename it to clean 'orders' for clarity
        if 'orders_tracking' in merged_df.columns:
            merged_df.rename(columns={'orders_tracking': 'orders'}, inplace=True)
        elif 'orders_x' in merged_df.columns:
            merged_df.rename(columns={'orders_x': 'orders'}, inplace=True)

        # Drop the payout-side orders unless needed
        if 'orders_payouts' in merged_df.columns:
            merged_df.drop(columns=['orders_payouts'], inplace=True)
        if 'orders_y' in merged_df.columns:
            merged_df.drop(columns=['orders_y'], inplace=True)

        # Ensure numeric types
        merged_df['revenue'] = pd.to_numeric(merged_df['revenue'], errors='coerce').fillna(0)
        merged_df['orders'] = pd.to_numeric(merged_df['orders'], errors='coerce').fillna(0)
        merged_df['total_payout'] = pd.to_numeric(merged_df['total_payout'], errors='coerce').fillna(0)

        # --- Step 5: Group by influencer ---
        incremental_df = merged_df.groupby('influencer_id', as_index=False).agg({
            'orders': 'sum',  # Sum of actual tracked orders
            'revenue': 'sum',  # Total revenue
            'total_payout': 'sum'  # Total payout
        })

        # --- Step 6: Calculate iROAS safely ---
        incremental_df['iROAS'] = (incremental_df['revenue'] / incremental_df['orders'])
        incremental_df['iROAS'] = incremental_df['iROAS'].replace([float('inf'), -float('inf')], 0).fillna(0)
        incremental_df['iROAS'] = incremental_df['iROAS'].round(2)

        # --- Step 7: Display result ---
        display_cols = ['influencer_id', 'orders', 'revenue', 'total_payout', 'iROAS']
        if not incremental_df.empty:
            st.dataframe(incremental_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("No incremental ROAS data matches the selected filters.")

except Exception as e:
    st.error(f"❌ Error calculating incremental ROAS: {str(e)}")
    if 'merged_df' in locals():
        st.write("**Columns after merge:**", merged_df.columns.tolist())
        st.write("**Sample data:**", merged_df.head())

# 📌 Insights – Performance Highlights
# ===================================
st.subheader("📌 Insights – Performance Highlights")

try:
    # ⭐ Top Influencers by ROAS
    top_influencers = roas_df.sort_values('roas', ascending=False).head(5)
    st.markdown("### ⭐ Top Influencers (by ROAS)")
    st.dataframe(top_influencers[['name', 'roas', 'total_revenue', 'total_payout']], use_container_width=True)

    # 🚩 Poor ROAS Performers
    poor_roas = roas_df[roas_df['roas'] < 1].sort_values('roas').head(5)
    st.markdown("### 🚩 Influencers with Poor ROAS (Below 1)")
    st.dataframe(poor_roas[['name', 'roas', 'total_revenue', 'total_payout']], use_container_width=True)

    # 🧠 Persona-Based Insights (excluding product)
    st.markdown("### 🧠 Persona-Based Insights")

    if 'roas' in roas_df.columns and not roas_df.empty:
        persona_df = roas_df.merge(filtered_influencers, left_on='influencer_id', right_on='id', how='inner')

        persona_columns = []
        if influencer_type_col and influencer_type_col in persona_df.columns:
            persona_columns.append(influencer_type_col)
        if 'gender' in persona_df.columns:
            persona_columns.append('gender')
        if 'platform' in persona_df.columns:
            persona_columns.append('platform')

        if persona_columns:
            for col in persona_columns:
                insights = persona_df.groupby(col)['roas'].agg(['mean', 'count']).reset_index()
                insights.columns = [col, 'avg_roas', 'count']
                insights = insights.sort_values('avg_roas', ascending=False)

                st.write(f"**Average ROAS by {col.title()}:**")
                col1, col2 = st.columns([2, 1])

                with col1:
                    if not insights.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        bars = ax.bar(insights[col], insights['avg_roas'], color='steelblue', alpha=0.7)
                        ax.set_xlabel(col.title())
                        ax.set_ylabel("Average ROAS")
                        ax.set_title(f"Average ROAS by {col.title()} (Filtered)")
                        plt.xticks(rotation=45)

                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width() / 2., height,
                                    f'{height:.2f}', ha='center', va='bottom')

                        plt.tight_layout()
                        st.pyplot(fig)

                with col2:
                    st.dataframe(insights, use_container_width=True, hide_index=True)

        else:
            st.warning("No persona columns (influencer type, gender, platform) available for analysis.")
    else:
        st.warning("ROAS data not available for persona insights.")

except Exception as e:
    st.error(f"Error in insights section: {e}")

# ===========================
# 📊 Filter Impact Summary
# ===========================
st.subheader("📊 Filter Impact Summary")

# Create summary metrics
total_revenue = filtered_tracking['revenue'].sum() if 'revenue' in filtered_tracking.columns else 0
total_orders = filtered_tracking['orders'].sum() if 'orders' in filtered_tracking.columns else 0
avg_roas = roas_df['roas'].mean() if 'roas' in roas_df.columns and not roas_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
with col2:
    st.metric("Total Orders", f"{total_orders:,}")
with col3:
    st.metric("Average ROAS", f"{avg_roas:.2f}")
with col4:
    efficiency = (total_revenue / len(filtered_influencers)) if len(filtered_influencers) > 0 else 0
    st.metric("Revenue per Influencer", f"₹{efficiency:,.2f}")

# Show active filters summary
st.info(f"""
**Active Filters Summary:**
- Platforms: {', '.join(selected_platform)}
- Campaigns: {', '.join(selected_campaign)}
{f"- Products: {len(selected_product)} selected" if selected_product else "- Products: All products included"}
{f"- Categories: {', '.join(selected_influencer_type)}" if selected_influencer_type else "- Categories: All categories included"}
{f"- Genders: {', '.join(selected_gender)}" if selected_gender else "- Genders: All genders included"}
{f"- Follower Range: {selected_follower_range[0]:,} - {selected_follower_range[1]:,}" if selected_follower_range else "- Followers: Full range included"}
""")
st.markdown("---")
st.markdown("*Use the sidebar filters to drill down into specific segments and discover insights!*")