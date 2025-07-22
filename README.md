# HealthKart Influencer Campaign Dashboard

An interactive Streamlit dashboard to **track influencer marketing performance**, analyze **ROAS (Return on Ad Spend)**, **incrementality**, and extract actionable insights. 

---

## Features

- Advanced sidebar filters (platform, product, campaign, influencer category, gender, follower count, date)
- Dynamic influencer and campaign performance summary
- ROAS, ROI, and iROAS (incremental ROAS) calculations
- Visualizations: ROAS comparison chart, persona-based insights
- Post performance tracker and influencer-level metrics
- Filter impact summary with a storytelling touch

---

## Data Schema

### Required CSV Files (to be placed in the `data/` folder)

#### 1. `influencers.csv`

| Column           | Description                              |
|------------------|------------------------------------------|
| `id`             | Unique influencer ID                     |
| `name`           | Influencer’s full name                   |
| `category`       | Niche/category                           | 
| `gender`         | Gender identity                          |
| `follower count` | Total followers                          |
| `platform`       | Platform used                            |

#### 2. `posts.csv`

| Column          | Description                             |
|-----------------|-----------------------------------------|
| `influencer_id` | Foreign key linking to `influencers.id` |
| `platform`      | Platform where the post was made        |
| `date`          | Date of the post                        |
| `url`           | Post URL                                |
| `caption`       | Post content/caption                    |
| `reach`         | Estimated reach                         |
| `likes`         | Number of likes                         |
| `comments`      | Number of comments                      |

#### 3. `tracking_data.csv`

| Column          | Description                             |
|-----------------|-----------------------------------------|
| `source`        | Traffic source/platform                 |
| `campaign`      | Campaign name                           |
| `influencer_id` | Foreign key linking to `influencers.id` |
| `user_id`       | Unique user ID                          |
| `product`       | Product name                            |
| `date`          | Date of order                           |
| `orders`        | Number of orders                        |
| `revenue`       | Revenue generated                       |

#### 4. `payouts.csv`

| Column          | Description                                      |
|-----------------|--------------------------------------------------|
| `influencer_id` | Foreign key linking to `influencers.id`          |
| `basis`         | Payout basis – either `post` or `order`          |
| `rate`          | Rate per post or per order                       |
| `orders`        | No. of posts or orders applicable for payout     |
| `total_payout`  | Final payout value                               |

---

## Data Handling Logic

- Flexible parsing of column name variants (`followers` or `follower_count`, `created_at` or `date`)
- Date fields auto-detected and converted using `pd.to_datetime()`
- All numeric fields (`revenue`, `orders`, `payout`, etc.) coerced into proper formats
- Handles nulls and formatting inconsistencies gracefully

---

## Setup Instructions

### 1. Install Dependencies

Make sure Python is installed. Then, install the required Python packages in your terminal:

```bash
pip install streamlit pandas matplotlib
```

### 2. Project Structure

```bash
healthkart_dashboard/
├── app.py                  # Main Streamlit dashboard script
├── data/
│   ├── influencers.csv
│   ├── posts.csv
│   ├── tracking_data.csv
│   └── payouts.csv
└── README.md               # This file
```

### 3. Run the Dashboard

In your terminal:

```bash
streamlit run app.py
```
