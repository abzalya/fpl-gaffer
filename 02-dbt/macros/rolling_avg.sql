-- rolling_avg
{% macro rolling_avg(column, partition_by, order_by, window_size) %}
    AVG({{ column }}) over (
        partition by {{ partition_by }}
        order by {{ order_by }}
        rows between {{ window_size - 1 }} preceding and current row)
{% endmacro %}