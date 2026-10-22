{% macro delta_source(table_path) %}
    {% if target.type == 'duckdb' %}
        delta_scan('{{ var("delta_base_path", "file:///data/delta") }}/{{ table_path }}')
    {% elif target.type == 'databricks' %}
        {{ var("databricks_catalog", "mydata") }}.{{ table_path | replace("/", "_") }}
    {% else %}
        {{ exceptions.raise_compiler_error("Unsupported adapter: " ~ target.type) }}
    {% endif %}
{% endmacro %}
