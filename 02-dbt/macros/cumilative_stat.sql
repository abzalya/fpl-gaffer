-- cumilative_stat
{% macro cumulative_sum(column, partition_by, order_by) %}
SUM({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }} asc
    rows between unbounded preceding and current row
  )
{% endmacro %}