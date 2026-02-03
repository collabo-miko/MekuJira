<script lang="ts">
	import { onMount } from 'svelte';
	import { getSessions, getDocuments, type Session, type Document } from '$lib/api/client';
	import StatusBadge from '$lib/components/StatusBadge.svelte';

	let sessions: Session[] = [];
	let documents: Document[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			[sessions, documents] = await Promise.all([getSessions(), getDocuments()]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'エラーが発生しました';
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleString('ja-JP');
	}
</script>

<svelte:head>
	<title>ダッシュボード - Security Check Assistant</title>
</svelte:head>

<div class="px-4 sm:px-0">
	<h1 class="text-2xl font-bold text-gray-900 mb-6">ダッシュボード</h1>

	{#if loading}
		<div class="text-center py-8">
			<div
				class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"
			></div>
			<p class="mt-2 text-gray-600">読み込み中...</p>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else}
		<!-- Quick Actions -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
			<a
				href="/upload"
				class="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
			>
				<div class="flex items-center">
					<div class="flex-shrink-0 bg-blue-100 rounded-lg p-3">
						<svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
							/>
						</svg>
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-medium text-gray-900">Excelアップロード</h3>
						<p class="text-sm text-gray-500">チェックシートをアップロード</p>
					</div>
				</div>
			</a>

			<a
				href="/documents"
				class="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
			>
				<div class="flex items-center">
					<div class="flex-shrink-0 bg-green-100 rounded-lg p-3">
						<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-medium text-gray-900">ドキュメント管理</h3>
						<p class="text-sm text-gray-500">{documents.length}件のドキュメント</p>
					</div>
				</div>
			</a>

			<div class="p-6 bg-white rounded-lg shadow">
				<div class="flex items-center">
					<div class="flex-shrink-0 bg-purple-100 rounded-lg p-3">
						<svg
							class="h-6 w-6 text-purple-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
							/>
						</svg>
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-medium text-gray-900">セッション</h3>
						<p class="text-sm text-gray-500">{sessions.length}件のセッション</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Recent Sessions -->
		<div class="bg-white shadow rounded-lg">
			<div class="px-4 py-5 sm:px-6 border-b">
				<h2 class="text-lg font-medium text-gray-900">最近のセッション</h2>
			</div>
			<div class="divide-y">
				{#if sessions.length === 0}
					<div class="px-4 py-8 text-center text-gray-500">
						セッションがありません。Excelファイルをアップロードしてください。
					</div>
				{:else}
					{#each sessions.slice(0, 10) as session}
						<a
							href="/review/{session.id}"
							class="block px-4 py-4 hover:bg-gray-50 transition-colors"
						>
							<div class="flex items-center justify-between">
								<div class="flex-1 min-w-0">
									<p class="text-sm font-medium text-gray-900 truncate">{session.filename}</p>
									<p class="text-sm text-gray-500">
										{session.vendor_name || '（ベンダー名なし）'} ・
										{session.total_questions}問 ・
										{formatDate(session.created_at)}
									</p>
								</div>
								<div class="flex items-center space-x-4">
									<span class="text-sm text-gray-500">
										{session.answered_questions}/{session.total_questions} 回答
									</span>
									<StatusBadge status={session.status} />
								</div>
							</div>
						</a>
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>
