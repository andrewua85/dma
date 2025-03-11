FORMULAS = {
    "ru": [
        (
            "CTR (Кликабельность)",
            "Кликабельность (CTR) — процент кликов от общего числа показов.",
            [
                ("Количество показов:", "ctr_impressions", "Общее количество показов рекламы"),
                ("Количество кликов:", "ctr_clicks", "Общее количество кликов по рекламе"),
            ]
        ),
        (
            "CPC (Стоимость за клик)",
            "Стоимость за клик (CPC) — затраты на один клик.",
            [
                ("Затраты на рекламу ($):", "cpc_total_cost", "Общие затраты на рекламу в долларах"),
                ("Количество кликов:", "cpc_clicks", "Общее количество кликов"),
            ]
        ),
        (
            "CPA (Стоимость за действие)",
            "Стоимость за действие (CPA) — затраты на одно целевое действие.",
            [
                ("Затраты на рекламу ($):", "cpa_total_cost", "Общие затраты на рекламу в долларах"),
                ("Количество конверсий:", "cpa_actions", "Общее количество целевых действий"),
            ]
        ),
        (
            "ROAS (Возврат затрат)",
            "Возврат затрат на рекламу (ROAS) — отношение дохода к затратам.",
            [
                ("Доход от рекламы ($):", "roas_revenue", "Общий доход от рекламы в долларах"),
                ("Затраты на рекламу ($):", "roas_total_cost", "Общие затраты на рекламу в долларах"),
            ]
        ),
        (
            "CR (Конверсия)",
            "Конверсия (CR) — процент конверсий от общего числа кликов.",
            [
                ("Количество кликов:", "cr_clicks", "Общее количество кликов"),
                ("Количество конверсий:", "cr_conversions", "Общее количество конверсий"),
            ]
        ),
        (
            "LTV (Пожизненная ценность клиента)",
            "LTV — это доход, который клиент приносит за всё время взаимодействия с компанией.",
            [
                ("Средний доход ($):", "ltv_avg_revenue", "Средний доход от клиента за одну покупку в долларах"),
                ("Количество покупок:", "ltv_purchases", "Среднее количество покупок клиента"),
                ("Период (лет):", "ltv_period", "Средний срок жизни клиента в годах"),
            ]
        ),
        (
            "CPL (Стоимость за лид)",
            "Стоимость за лид (CPL) — затраты на одного лида.",
            [
                ("Затраты на рекламу ($):", "cpl_total_cost", "Общие затраты на рекламу в долларах"),
                ("Количество лидов:", "cpl_leads", "Общее количество лидов"),
            ]
        ),
        (
            "RPM (Доход на тысячу показов)",
            "Доход на тысячу показов (RPM) — доход с 1000 показов.",
            [
                ("Доход от рекламы ($):", "rpm_revenue", "Общий доход от рекламы в долларах"),
                ("Количество показов:", "rpm_impressions", "Общее количество показов рекламы"),
            ]
        ),
    ],
    "en": [
        (
            "CTR (Click-Through Rate)",
            "Click-Through Rate (CTR) — the percentage of clicks from total impressions.",
            [
                ("Number of Impressions:", "ctr_impressions", "Total number of ad impressions"),
                ("Number of Clicks:", "ctr_clicks", "Total number of clicks on the ad"),
            ]
        ),
        (
            "CPC (Cost Per Click)",
            "Cost Per Click (CPC) — the cost per one click.",
            [
                ("Advertising Cost ($):", "cpc_total_cost", "Total advertising cost in dollars"),
                ("Number of Clicks:", "cpc_clicks", "Total number of clicks"),
            ]
        ),
        (
            "CPA (Cost Per Action)",
            "Cost Per Action (CPA) — the cost of one target action.",
            [
                ("Advertising Cost ($):", "cpa_total_cost", "Total advertising cost in dollars"),
                ("Number of Conversions:", "cpa_actions", "Total number of target actions"),
            ]
        ),
        (
            "ROAS (Return on Ad Spend)",
            "Return on Ad Spend (ROAS) — the ratio of revenue to advertising cost.",
            [
                ("Advertising Revenue ($):", "roas_revenue", "Total revenue from advertising in dollars"),
                ("Advertising Cost ($):", "roas_total_cost", "Total advertising cost in dollars"),
            ]
        ),
        (
            "CR (Conversion Rate)",
            "Conversion Rate (CR) — the percentage of conversions from total clicks.",
            [
                ("Number of Clicks:", "cr_clicks", "Total number of clicks"),
                ("Number of Conversions:", "cr_conversions", "Total number of conversions"),
            ]
        ),
        (
            "LTV (Lifetime Value)",
            "LTV — the revenue a customer brings over their entire relationship with the company.",
            [
                ("Average Revenue ($):", "ltv_avg_revenue", "Average revenue per purchase in dollars"),
                ("Number of Purchases:", "ltv_purchases", "Average number of purchases per customer"),
                ("Period (years):", "ltv_period", "Average customer lifespan in years"),
            ]
        ),
        (
            "CPL (Cost Per Lead)",
            "Cost Per Lead (CPL) — the cost per one lead.",
            [
                ("Advertising Cost ($):", "cpl_total_cost", "Total advertising cost in dollars"),
                ("Number of Leads:", "cpl_leads", "Total number of leads"),
            ]
        ),
        (
            "RPM (Revenue Per Mille)",
            "Revenue Per Mille (RPM) — revenue per 1000 impressions.",
            [
                ("Advertising Revenue ($):", "rpm_revenue", "Total revenue from advertising in dollars"),
                ("Number of Impressions:", "rpm_impressions", "Total number of ad impressions"),
            ]
        ),
    ]
}