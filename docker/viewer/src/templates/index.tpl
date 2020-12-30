<!DOCTYPE html>
<html>
    <head>
        <title>Lliurex Analytics</title>
        <link href="/analytics/static/favicon.ico" rel="shortcut icon">
        {%- for item in csslib -%}
        <link href="{{ item }}.css" rel="stylesheet">
        {%- endfor -%}

        {%- for item in jslib -%}
        <script type="text/javascript" src="{{ item }}.js"></script>
        {%- endfor -%}
        
        {%- for item in jscmd -%}
        <script type="text/javascript">
            {{ item }}
        </script>
        {%- endfor %}
    </head>
    <body>
        <ul id="navigation">
        <span class="title">Llliurex Analytics</span>
        {%- for item in navigation -%}
            <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
        {%- endfor -%}
        </ul>
        <div id="header">
            <div id="query_box"></div>
            <div id="stats_box"></div>
        </div>
        <div id="accordion">
        </div>
    </body>
</html>