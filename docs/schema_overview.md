{% import 'macros/schema_table.html' as st %}
{% set schema = load_yaml('schema/raw/schema.yaml') %}

# Database Schema Overview

Parsed from `docs/schema/raw/schema.yaml`.

{% for t in schema.database_schema.tables %}
## Table: {{ t.table }}

{{ st.render_table(t) }}
{% endfor %}

