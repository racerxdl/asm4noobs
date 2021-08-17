---
title: "Chamadas de sistema Linux AMD64"
date: 2020-08-02T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /syscall/linux-amd64
tags:
  - x86
  - intel
  - amd
  - syscall
  - exit
---

Aqui serão listadas as chamadas de sistema do kernel linux da arquitetura AMD64. Esse arquivo foi gerado automaticamente usando o código fonte do kernel no github. Para mais detalhes, veja a pasta `_generator` no github do asm4noobs.

O conteúdo desta página pode ser lido programaticamente usando o arquivo [syscalls_linux_amd64.json](/syscalls_linux_amd64.json)

## Ordem dos argumentos

<table>
	<tr>
		<th>#</th>
		{% assign i = 0 %}
		{% for reg in site.data.syscalls_linux_amd64.argRegs %}
		<th> {{ i }}</th>
    	{% assign i = i | plus:1 %}
		{% endfor %}
	</tr>
	<tr>
		<td>Registrador</td>
		{% for reg in site.data.syscalls_linux_amd64.argRegs %}
		<td> {{ reg }}</td>
		{% endfor %}
	</tr>
</table>

{% for syscall in site.data.syscalls_linux_amd64.syscalls %}

<div id="syscall_{{ syscall.id }}">

<h2> {{ syscall.id }} - {{ syscall.name }} </h2>

<ul>
	<li>Número (RAX): <b>{{ syscall.id }}</b></li>
	<li>Arquivo: <a href="https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/{{ syscall.filename }}">{{ syscall.filename }}</a></li>
	<li>Entrypoint: {{ syscall.entry }}</li>
	<li>Argumentos:</li>
</ul>

<table>
	<tr>
		<th>#</th>
		<th>Tipo</th>
		<th>Nome</th>
		<th>Registrador</th>
	</tr>
	{% for arg in syscall.args %}
	<tr>
		<td>{{ arg.idx }}</td>
		<td>{{ arg.type }}</td>
		<td>{{ arg.name }}</td>
		<td>{{ arg.reg }}</td>
	</tr>
	{% endfor %}
</table>
</div>
{% endfor %}

