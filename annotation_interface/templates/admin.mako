## -*- coding: utf-8 -*-
<%inherit file="index.mako"/>
<%block name="nav">

</%block>
<%block name="content">
    <div>
        <h2>Evaluation</h2>
        <table>
            <tr><th>Right answer</th><td>${score[0]}</td></tr>
            <tr><th>Wrong answer</th><td>${score[1]}</td></tr>
            <tr><th>Accuracy</th><td>${100.0 * score[0] / max(1, score[1])}%</td></tr>
        </table>

        <h2>Annotators</h2>
        <table>
            <tr><th>annotator</th><th>supported answer</th><th>unique answer</th><th>no answer</th></tr>
            % for user, (agree, disagree, skip) in agreement.iteritems():
                <tr><td>${user}</td><td>${agree}</td><td>${disagree}</td><td>${skip}</td></tr>
            % endfor

        </table>

        <h2>Export</h2>
        <table>
            <tr>
                <th>Task id</th>
                <th>Model id</th>
                <th>Topic id</th>
                <th>Variants</th>
                <th>Intrusion</th>
                <th>Annotations</th>
                <th>User choice</th>
            </tr>
            % for task_id, model_id, topic_no, task, alg_answer, user_answers in export:
                <%
                    user_choice = sorted(
                        [(a, user_answers.count(a)) for a in user_answers],
                        key=lambda (a, v): -v + 1000 if '?' in a or '!' in a else 0
                        )[0][0]
                %>
                <tr>
                    <td>${task_id}</td>
                    <td>${model_id}</td>
                    <td>${topic_no}</td>
                    <td>${task}</td>
                    <td style="background-color: ${'green' if user_choice == alg_answer else 'red'}">${alg_answer}</td>
                    <td>${' '.join(user_answers)}</td>
                    <td>${user_choice}</td>
                </tr>
            % endfor

        </table>

    </div>


</%block>
<%block name="footer">
        <script>



            function update(al) {

            }

            document.onload = update();
        </script>


</%block>
