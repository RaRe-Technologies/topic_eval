## -*- coding: utf-8 -*-
<!doctype html>

<html lang="cs">
<head>
    <meta charset="utf-8">

    <title>Job listings annotation</title>
    <meta name="description" content="Anotování">
    <meta name="author" content="Jan Rygl">
    <link href="css/video-js.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="css/styles.css?v=1.0">
    <link rel="stylesheet" href="static/base.css?v=1.0">
    <link href='http://fonts.googleapis.com/css?family=Open+Sans&subset=latin,latin-ext'
        rel='stylesheet' type='text/css'>
    <!--[if lt IE 9]>
    <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
</head>

<body>
    <header>
        <h1>Word intrusion detection</h1>
        | <a href="/">next task</a>
        | <a href="/help">annotation manual</a>
        %if "username" in session:
            | logged as <strong>${session.get("username")}</strong> |
            <a href="logout">log out</a>
        %endif
        %if stats:
            | Done: ${stats.get('done', '?')} | Skipped: ${stats.get('skipped', '?')}
        %endif

    </header>
    <nav>
        <%block name="nav" />
    </nav>
    <main>
    % if error is not None:
        <p class="error">${error}</p>
    % else:
        <%block name="content" />
    % endif
    </main>

    <footer style="background-color: white; padding: 2ex; clear-both; margin-top: 5em">
        <%block name="footer">

        </%block>
    </footer>

</body>
</html>