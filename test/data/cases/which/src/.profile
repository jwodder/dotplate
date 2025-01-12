export EDITOR={{ which('nvim', 'vim', 'vi', 'sensible-editor') }}
{%- set less = which('less') -%}
{% if less is defined -%}
export PAGER={{ less }}
{% endif -%}
