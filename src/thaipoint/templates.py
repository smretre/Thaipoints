APP_TABS_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thaipoint App</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
.screen { display: none; }
.screen.active { display: block; }
</style>
</head>
<body class="bg-black text-white min-h-screen pb-20">

<!-- Home -->
<div id="home" class="screen active p-4 space-y-6">

  <!-- Seção de boas-vindas -->
  <div class="bg-neutral-900 p-6 rounded-2xl shadow-lg text-center space-y-2">
    <h1 class="text-3xl font-bold text-yellow-400">Bem-vindo ao Thaipoint!</h1>
    <p class="text-neutral-400">O app que conecta você às melhores lojas de Tailândia-PA em um só lugar.</p>
    <p class="text-neutral-400 text-sm">Explore produtos, acompanhe pedidos e finalize suas compras com segurança.</p>
  </div>

  <!-- Seção de destaques/lojas -->
  <h2 class="text-2xl font-bold text-white">Lojas em Destaque</h2>
  <div class="grid sm:grid-cols-2 gap-4">
    {% for store in stores %}
    <div class="bg-neutral-800 p-4 rounded-2xl shadow-md hover:scale-105 transition-transform duration-200">
      <div class="flex justify-between items-center mb-2">
        <span class="font-semibold text-white text-lg">{{ store.name }}</span>
        <span class="text-sm bg-yellow-400 text-black px-2 py-1 rounded">{{ store.type }}</span>
      </div>
      <div class="text-neutral-400 text-sm mb-3">{{ store.bairro }}</div>
      <button onclick="showStore('{{ store.id }}')" class="w-full bg-red-500 hover:bg-red-600 px-4 py-2 rounded-xl font-semibold">Ver Produtos</button>
    </div>
    {% endfor %}
  </div>

  <!-- Seção de confiança -->
  <div class="bg-neutral-900 p-6 rounded-2xl shadow-lg mt-6 space-y-2 text-center">
    <h3 class="text-xl font-bold text-white">Por que escolher o Thaipoint?</h3>
    <ul class="text-neutral-400 list-disc list-inside space-y-1">
      <li>✅ Produtos de qualidade das melhores lojas da cidade</li>
      <li>✅ Pagamento seguro e fácil</li>
      <li>✅ Acompanhe seu pedido em tempo real</li>
      <li>✅ Atendimento dedicado ao cliente</li>
    </ul>
  </div>

  <!-- Call-to-action -->
  <div class="text-center mt-4">
    <button onclick="showScreen('search')" class="bg-yellow-400 text-black font-bold px-6 py-3 rounded-full shadow-lg hover:bg-yellow-500 transition-colors">Comece a Buscar Produtos</button>
  </div>

</div>

<!-- Search -->
<div id="search" class="screen p-4 space-y-4">
  <h1 class="text-2xl font-bold mb-2">Pesquisar Produto</h1>
  <input id="searchInput" type="text" placeholder="Nome do produto" class="w-full p-3 rounded-lg bg-neutral-800 border border-neutral-700"/>
  <button onclick="searchProduct()" class="bg-red-500 px-4 py-2 rounded-xl mt-2">Buscar</button>
  <div id="searchResults" class="mt-4 space-y-2"></div>
</div>

<!-- Cart -->
<div id="cart" class="screen p-4 space-y-4">
  <h1 class="text-2xl font-bold mb-2">Carrinho ({{ cart|length }})</h1>
  {% if cart %}
  {% set subtotal=0 %}
  {% for item in cart %}
  {% set subtotal = subtotal + item.price*item.qty %}
  <div class="flex justify-between items-center bg-neutral-800 p-3 rounded-xl mb-2">
    <div>
      <div>{{ item.name }}</div>
      <div class="text-yellow-400">R$ {{ item.price }} x {{ item.qty }}</div>
    </div>
    <a href="{{ url_for('remove_item', product_id=item.id) }}" class="bg-red-600 px-3 py-1 rounded-xl font-semibold">Remover</a>
  </div>
  {% endfor %}
  <div class="font-semibold mb-2">Subtotal: R$ {{ subtotal }}</div>
  <button onclick="showScreen('payment')" class="w-full bg-red-500 py-3 rounded-xl mt-2 font-bold">Finalizar Pedido</button>
  {% else %}
  <div class="text-neutral-400">Seu carrinho está vazio.</div>
  {% endif %}
</div>

<!-- Order -->
<div id="order" class="screen p-4 space-y-4">
  <h1 class="text-2xl font-bold mb-2">Acompanhar Pedido</h1>
  {% if active_order %}
  <div>Status: {{ active_order.status }}</div>
  <div class="h-3 bg-neutral-800 rounded-full overflow-hidden mb-1">
    <div class="h-full bg-red-500" style="width:{{ progress }}%"></div>
  </div>
  <div>Chegada prevista: {{ active_order.eta }}</div>
  {% else %}
  <div class="text-neutral-400">Nenhum pedido ativo.</div>
  {% endif %}
</div>

<!-- Payment -->
<div id="payment" class="screen p-4 space-y-4">
  <h1 class="text-2xl font-bold mb-2">Pagamento Simulado</h1>
  <select id="paymentMethod" class="w-full p-3 rounded-lg bg-neutral-800 border border-neutral-700">
    <option value="pix">PIX</option>
    <option value="cartao">Cartão</option>
    <option value="dinheiro">Dinheiro</option>
  </select>
  <button onclick="payOrder()" class="w-full bg-red-500 py-3 rounded-xl mt-2 font-bold">Pagar</button>
</div>

<!-- Tab Menu -->
<nav class="fixed bottom-0 left-0 w-full bg-neutral-900 border-t border-neutral-700 flex justify-around py-3">
  <button onclick="showScreen('home')">🏠</button>
  <button onclick="showScreen('search')">🔍</button>
  <button onclick="showScreen('cart')">🛒</button>
  <button onclick="showScreen('order')">📦</button>
</nav>

<script>
function showScreen(id){
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function searchProduct(){
  const q = document.getElementById('searchInput').value.toLowerCase();
  const resultsDiv = document.getElementById('searchResults');
  resultsDiv.innerHTML = '';
  let found = false;
  {% for store in stores %}
    {% for p in store.products %}
      if('{{ p.name.lower() }}'.includes(q)){
        resultsDiv.innerHTML += `<div class="bg-neutral-800 p-3 rounded-xl flex justify-between">
          <div>${'{{ p.name }}'} - R$ {{ p.price }}</div>
          <a href="{{ url_for('add_to_cart', store_id=store.id, product_id=p.id) }}" class="bg-red-500 px-3 py-1 rounded-xl">Adicionar</a>
        </div>`;
        found = true;
      }
    {% endfor %}
  {% endfor %}
  if(!found) resultsDiv.innerHTML = '<div class="text-neutral-400">Produto não encontrado</div>';
}

function payOrder(){
  alert("Pagamento realizado com sucesso! 🎉");
  showScreen('home');
}
</script>
</body>
</html>
"""

