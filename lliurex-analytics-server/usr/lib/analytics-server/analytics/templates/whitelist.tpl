<!DOCTYPE html>
<html>
    <head>
        <title>Lliurex Analytics</title>
        <link href="favicon.ico" rel="shortcut icon">
        {% for item in csslib %}<link href="{{ item|raw }}.css" rel="stylesheet">
        {% endfor %}

        {% for item in jslib %}<script type="text/javascript" src="{{ item|raw }}.js"></script>
        {% endfor %}

        {% for item in jscmd %}<script type="text/javascript">
            {{ item|raw }}
        </script>
        {% endfor %}
    </head>
    <body>
        <ul id="navigation">
        <span class="title">Llliurex Analytics</span>
        {% for item in navigation %}
            <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
        {% endfor %}
        </ul>
        <div id='configure_whitelist'>
            <div id='nonwhitelist'>
                <span>Not in whitelist</span>
                <div id='filternot' class='filter'>Filter:<textarea rows='1'></textarea></div>
                <select name='denied' multiple>
                </select>
            </div>
            <div id='btn_left'>
                <button id='btnleft_to_left'>&lt;&lt;&lt;</button>
                <button id='btnleft_to_center'>&gt;&gt;&gt;</button>
            </div>
            <div id='unknown_state_whitelist'>
                <span>New elements</span>
                <div id='filterunk' class='filter'>Filter:<textarea rows='1'></textarea></div>
                <select name='nonselected' multiple>
                </select>
            </div>
            <div id='btn_right'>
                <button id='btnright_to_right'>&gt;&gt;&gt;</button>
                <button id='btnright_to_center'>&lt;&lt;&lt;</button>
            </div>
            <div id='inwhitelist'>
                <span>In whitelist</span>
                <div id='filterin' class='filter'>Filter:<textarea rows='1'></textarea></div>
                <select name='accepted' multiple>
                </select>
            </div>
        </div>
        <div id='send'>
            <button id='send_btn'>Apply</button>
        </div>
    </body>
</html>