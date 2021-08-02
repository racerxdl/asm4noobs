
Este repositório é um tutorial dedicado ao ensino da linguagem assembly! Sejam bem-vindos a baixaria!

** WORK IN PROGRESS **

Conteúdo
========

* [Assembly]
  * [O que é Assembly?]
  * [Um simples processador]
  * [Uma simples memória]
  * [Códigos de Operação]
* [X86 (AMD/Intel)]
  * [Pequena história]
  * [Estrutura Básica do Processador]
* [ARM64 (Raspberry PI / Android)]
  * [Pequena história]
  * [Estrutura Básica do Processador]
* [RISC-V]
  * [Pequena história]
  * [Estrutura Básica do Processador]
* Referências
  * [Opcodes X86](/opcodes/x86)
  * [Opcodes ARM 32 bits](/opcodes/arm)
  * [Opcodes ARM 64 bits](/opcodes/arm64)
  * [Opcodes RISC-V](/opcodes/riscv)



<div class="catalogue">
  {% for post in paginator.posts %}
    <a href="{{ post.url | prepend: site.baseurl }}" class="catalogue-item catalogue-item-2">
      <div>
        <time datetime="{{ post.date }}" class="catalogue-time">{{ post.date | date: "%B %d, %Y" }}</time>
        <h1 class="catalogue-title">{{ post.title }}</h1>
        <div class="catalogue-line"></div>
        {% if post.image %}
          <div class="post-image-div">
            <img src="{{ post.image }}" class="post-image post-image-2"/>
          </div>
        {% endif %}
        <p>
          {{ post.content | strip_html | truncatewords: 100 }}
        </p>

      </div>
    </a>
  {% endfor %}
</div>

<div class="pagination">
  {% if paginator.previous_page %}
    <a href="{{ paginator.previous_page_path | prepend: site.baseurl }}" class="left arrow">&#8592;</a>
  {% endif %}
  {% if paginator.next_page %}
    <a href="{{ paginator.next_page_path | prepend: site.baseurl }}" class="right arrow">&#8594;</a>
  {% endif %}

  <span>{{ paginator.page }}</span>
</div>
