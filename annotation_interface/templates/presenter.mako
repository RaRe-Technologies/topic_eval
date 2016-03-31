## -*- coding: utf-8 -*-
<%inherit file="index.mako"/>
<%block name="nav">

</%block>
<%block name="content">
    % if input is None:
        <span>The task is finished. Thanks for your work.</span>
    % else:
        <form method="post" style="margin: 0; padding: 0">
            <input type="hidden" value="${input['task_id']}" name="_task_id" id="_task_id" />
            <input type="hidden" value="${input['model_id']}" name="_model_id" id="_model_id" />
            <input type="hidden" value="${input['task']}" name="_task" id="_task" />
            <input type="hidden" value="${input['topic_no']}" name="_topic_no" id="_topic_no" />
            <input type="hidden" value="${input['answer']}" name="_answer" id="_answer" />
            <div class="">
                % for task_name in input['task'].split(' '):
                    <div class="control">
                        <input type="submit" id="${task_name}" value="${task_name}" name="${task_name}"
                           class="light" style="width: 220px; height: 35px; border: 1px solid grey;" />
                    </div>
                % endfor
                <div class="control">
                    <input type="submit" id="?" value="More than unknown word" name="?"
                       class="red" style="width: 220px; height: 35px; border: 1px solid grey;" />
                </div>
                <div class="control">
                    <input type="submit" id="!" value="No common theme" name="!"
                       class="red" style="width: 220px; height: 35px; border: 1px solid grey;" />
                </div>
            </div>

        </form>
    % endif
</%block>
