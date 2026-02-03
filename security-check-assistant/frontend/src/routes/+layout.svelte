<script>
	import '../app.css';
</script>

<div class="min-h-screen flex flex-col">
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<a href="/" class="text-xl font-bold text-gray-900"> Security Check Assistant </a>
				</div>
				<nav class="flex space-x-4">
					<a
						href="/"
						class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
					>
						ダッシュボード
					</a>
					<a
						href="/documents"
						class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
					>
						ドキュメント
					</a>
					<a
						href="/upload"
						class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
					>
						アップロード
					</a>
				</nav>
			</div>
		</div>
	</header>

	<main class="flex-1">
		<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
			<slot />
		</div>
	</main>

	<footer class="bg-white border-t">
		<div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
			<p class="text-center text-sm text-gray-500">Security Check Assistant v0.1.0</p>
		</div>
	</footer>
</div>
