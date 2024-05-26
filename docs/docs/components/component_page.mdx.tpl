---
title: {{ name }}
---

{{ description }}

<img src="/public/components/{{type}}.png" />

{{ docs }}

{% if fields %}
## Fields

<table>
	<thead>
		<td>Name</td>
		<td>Type</td>
		<td>Description</td>
		<td>Options</td>
	</thead>
	{% for _, field in fields %}
	<tr>
		<td>{{ field.name }}</td>
		<td>{{ field.type }}</td>
		<td>{{ field.desc }}</td>
		<td>
			<ul>
				{% for _, option in field.options %}
				<li>{{ option }}</li>
				{% endfor %}
			</ul>
		</td>
	</tr>
	{% endfor %}
</table>
{% endif %}

{% if events %}
## Events
<table>
	<thead>
		<td>Name</td>
		<td>Description</td>
		<td>Usage</td>
	</thead>
	{% for event, eventInfo in events %}
	<tr>
		<td>{{ event }}</td>
		<td>{{ eventInfo.desc }}</td>
		<td>
```python
{{ eventInfo.stub | safe }}
```
		</td>
	</tr>
	{% endfor %}
</table>
{% endif %}

## Low code usage

This component can be declared directly in Python, using [backend-driven UI](../backend-driven-ui).

```python
{{ low_code_usage | safe }}
```

{% if events %}
A function, in this example `handle_event`, should be implemented in your code to handle events.
```python
{{ event_handler | safe }}
```
{% endif %}


## Reference

* <a href="https://github.com/streamsync-cloud/streamsync/blob/dev/src/ui/{{fileRef}}" target="_blank" >Explore this component's source code on GitHub</a>
