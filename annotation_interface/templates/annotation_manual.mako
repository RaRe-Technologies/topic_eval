## -*- coding: utf-8 -*-
<%inherit file="index.mako"/>

<%block name="content">
    <div class="padded">
        <h2>Annotation manual</h2>

        <h3>Task description</h3>
        <ul>
            <li>Select a frame containing a word that not match semantic meaning of other words.</li>
            <li>If you really have no idea, select <i>I don't know</i> option. Please select it only rarely.</li>
            <li>If there are more non-matching words or there is no common semantic meaning between words,
                select <i>No solution</i> option. Please select it only rarely, words should have some semantic
                connection in all cases.</li>
        </ul>


        <h3>Examples</h3>

        <div style="border: 1px dotted grey; margin: 1ex; padding: 1ex ">
            <p style='font-family: "Courier New", courier, monospace'>
                bathroom closet attic balcony quickly toilet
            </p>
            <p>Select:<code>
                quickly
            </code>
                not a part of the house
            </p>
        </div>

        <div style="border: 1px dotted grey; margin: 1ex; padding: 1ex ">
            <p style='font-family: "Courier New", courier, monospace'>
                hockey february science ff align
            </p>
            <p>Select:<code>
                No solution
            </code>
                there are three groups: hockey + february (winter); science; ff + align (css)
            </p>
        </div>

        <div style="border: 1px dotted grey; margin: 1ex; padding: 1ex ">
            <p style='font-family: "Courier New", courier, monospace'>
                country musician island capital school
            </p>
            <p>Select:<code>
                musician
            </code>
                not a location
            </p>
        </div>
    </div>
</%block>