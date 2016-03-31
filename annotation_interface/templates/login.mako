## -*- coding: utf-8 -*-
<%inherit file="index.mako"/>
<%block name="nav">
</%block>
<%block name="content">
    <div style="text-align: center">
    <form method="post">
        <p>
            <label for="username">Surname</label> <input type="text" id="username" name="username">
        </p>
        <p>
            <label for="password">Password</label> <input type="password" id="password" name="password">
        </p>
        <p>
            <input type="submit" value="Log in" />
        </p>
        %if login_error:
            <p class="red">${login_error}</p>
        %endif
    </form>
    </div>
</%block>
