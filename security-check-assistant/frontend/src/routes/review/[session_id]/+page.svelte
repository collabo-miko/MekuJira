<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import {
		getReviewItems,
		getGenerationStatus,
		approveAnswer,
		modifyAnswer,
		finalizeSession,
		getExportUrl,
		getSessionFile,
		type ReviewItem,
		type ReviewResponse
	} from '$lib/api/client';
	import ConfidenceBadge from '$lib/components/ConfidenceBadge.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import ExcelPreview from '$lib/components/ExcelPreview.svelte';

	let review: ReviewResponse | null = null;
	let loading = true;
	let error: string | null = null;
	let editingId: string | null = null;
	let editText = '';
	let expandedSources: Set<string> = new Set();
	let pollInterval: number | null = null;
	let activeTab: 'review' | 'preview' = 'review';
	let excelFile: File | null = null;
	let loadingExcel = false;

	$: sessionId = $page.params.session_id;

	onMount(async () => {
		await loadReview();
	});

	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});

	async function loadReview() {
		try {
			loading = true;
			error = null;

			// Check generation status first
			const status = await getGenerationStatus(sessionId);

			if (status.status === 'generating') {
				// Poll for completion
				startPolling();
				return;
			}

			review = await getReviewItems(sessionId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'エラーが発生しました';
		} finally {
			loading = false;
		}
	}

	function startPolling() {
		if (pollInterval) return;

		pollInterval = setInterval(async () => {
			try {
				const status = await getGenerationStatus(sessionId);
				if (status.status !== 'generating') {
					if (pollInterval) clearInterval(pollInterval);
					pollInterval = null;
					await loadReview();
				}
			} catch (e) {
				if (pollInterval) clearInterval(pollInterval);
				pollInterval = null;
			}
		}, 2000) as unknown as number;
	}

	function startEdit(item: ReviewItem) {
		editingId = item.question_id;
		editText = item.answer_text;
	}

	function cancelEdit() {
		editingId = null;
		editText = '';
	}

	async function saveEdit(item: ReviewItem) {
		if (!item.answer_id) return;

		try {
			await modifyAnswer(item.answer_id, editText);
			await loadReview();
		} catch (e) {
			error = e instanceof Error ? e.message : '保存に失敗しました';
		} finally {
			editingId = null;
			editText = '';
		}
	}

	async function handleApprove(item: ReviewItem) {
		if (!item.answer_id) return;

		try {
			await approveAnswer(item.answer_id);
			await loadReview();
		} catch (e) {
			error = e instanceof Error ? e.message : '承認に失敗しました';
		}
	}

	async function handleFinalize() {
		if (!confirm('全ての承認済み回答を確定してナレッジベースに保存しますか？')) return;

		try {
			const result = await finalizeSession(sessionId);
			alert(`${result.knowledge_items_created}件の回答がナレッジベースに保存されました`);
			await loadReview();
		} catch (e) {
			error = e instanceof Error ? e.message : '確定に失敗しました';
		}
	}

	function toggleSources(questionId: string) {
		if (expandedSources.has(questionId)) {
			expandedSources.delete(questionId);
		} else {
			expandedSources.add(questionId);
		}
		expandedSources = expandedSources;
	}

	function downloadExcel() {
		window.location.href = getExportUrl(sessionId);
	}

	async function loadExcelFile() {
		if (excelFile || loadingExcel) return;
		loadingExcel = true;
		try {
			excelFile = await getSessionFile(sessionId);
		} catch (e) {
			console.error('Failed to load Excel file:', e);
		} finally {
			loadingExcel = false;
		}
	}

	function switchToPreviewTab() {
		activeTab = 'preview';
		loadExcelFile();
	}

	$: approvedCount = review?.items.filter(
		(i) => i.status === 'approved' || i.status === 'modified'
	).length ?? 0;
	$: pendingCount = review?.items.filter((i) => i.status === 'pending').length ?? 0;
</script>

<svelte:head>
	<title>レビュー - Security Check Assistant</title>
</svelte:head>

<div class="px-4 sm:px-0">
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
			<p class="mt-4 text-gray-600">
				{#if pollInterval}
					回答を生成中... しばらくお待ちください
				{:else}
					読み込み中...
				{/if}
			</p>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else if review}
		<!-- Header -->
		<div class="flex justify-between items-start mb-6">
			<div>
				<h1 class="text-2xl font-bold text-gray-900">{review.filename}</h1>
				<p class="text-gray-500">
					{review.vendor_name || '（ベンダー名なし）'} ・ {review.total_questions}問
				</p>
			</div>
			<div class="flex space-x-4">
				<a
					href="/report/{sessionId}"
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
				>
					レポート
				</a>
				<button
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
					on:click={downloadExcel}
				>
					Excelダウンロード
				</button>
				<button
					class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
					on:click={handleFinalize}
					disabled={approvedCount === 0}
				>
					確定（{approvedCount}件）
				</button>
			</div>
		</div>

		<!-- Summary -->
		<div class="bg-white shadow rounded-lg p-4 mb-6 flex space-x-8">
			<div>
				<span class="text-sm text-gray-500">合計</span>
				<span class="ml-2 font-medium">{review.total_questions}</span>
			</div>
			<div>
				<span class="text-sm text-gray-500">承認済み</span>
				<span class="ml-2 font-medium text-green-600">{approvedCount}</span>
			</div>
			<div>
				<span class="text-sm text-gray-500">未承認</span>
				<span class="ml-2 font-medium text-yellow-600">{pendingCount}</span>
			</div>
		</div>

		<!-- Tabs -->
		<div class="border-b border-gray-200 mb-6">
			<nav class="-mb-px flex space-x-8">
				<button
					type="button"
					class="py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'review'
						? 'border-blue-500 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					on:click={() => (activeTab = 'review')}
				>
					回答レビュー
				</button>
				<button
					type="button"
					class="py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'preview'
						? 'border-blue-500 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					on:click={switchToPreviewTab}
				>
					Excelプレビュー
				</button>
			</nav>
		</div>

		{#if activeTab === 'preview'}
			<!-- Excel Preview Tab -->
			<div class="bg-white shadow rounded-lg p-4">
				{#if loadingExcel}
					<div class="flex items-center justify-center py-8">
						<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
						<span class="ml-2 text-gray-600">Excelファイルを読み込み中...</span>
					</div>
				{:else if excelFile}
					<ExcelPreview file={excelFile} maxRows={100} />
				{:else}
					<div class="text-gray-500 text-center py-8">
						Excelファイルを読み込めませんでした
					</div>
				{/if}
			</div>
		{:else}
			<!-- Review Items Tab -->
			<div class="space-y-4">
			{#each review.items as item}
				<div
					class="bg-white shadow rounded-lg overflow-hidden border-l-4
						{item.confidence_level === 'high'
						? 'border-green-500'
						: item.confidence_level === 'medium'
							? 'border-yellow-500'
							: 'border-red-500'}"
				>
					<div class="p-4">
						<div class="flex justify-between items-start mb-2">
							<div class="flex items-center space-x-2">
								<span class="text-sm text-gray-500">#{item.row_number}</span>
								<ConfidenceBadge score={item.confidence_score} level={item.confidence_level} />
								<StatusBadge status={item.status} />
							</div>
							{#if item.sources.length > 0}
								<button
									class="text-sm text-blue-600 hover:text-blue-800"
									on:click={() => toggleSources(item.question_id)}
								>
									{expandedSources.has(item.question_id) ? '根拠を隠す' : '根拠を表示'}
								</button>
							{/if}
						</div>

						<p class="font-medium text-gray-900 mb-2">{item.question_text}</p>

						{#if item.remarks}
							<p class="text-sm text-gray-500 mb-2">備考: {item.remarks}</p>
						{/if}

						{#if editingId === item.question_id}
							<div class="mt-2">
								<textarea
									bind:value={editText}
									class="w-full px-3 py-2 border border-gray-300 rounded-md"
									rows="3"
								></textarea>
								<div class="mt-2 flex space-x-2">
									<button
										class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
										on:click={() => saveEdit(item)}
									>
										保存
									</button>
									<button
										class="px-3 py-1 border border-gray-300 text-sm rounded hover:bg-gray-50"
										on:click={cancelEdit}
									>
										キャンセル
									</button>
								</div>
							</div>
						{:else}
							<div class="bg-gray-50 rounded p-3 mt-2">
								<p class="text-gray-800 whitespace-pre-wrap">
									{item.answer_text || '（回答なし）'}
								</p>
							</div>
							<div class="mt-2 flex space-x-2">
								{#if item.answer_id && item.status === 'pending'}
									<button
										class="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
										on:click={() => handleApprove(item)}
									>
										承認
									</button>
								{/if}
								<button
									class="px-3 py-1 border border-gray-300 text-sm rounded hover:bg-gray-50"
									on:click={() => startEdit(item)}
								>
									編集
								</button>
							</div>
						{/if}

						{#if expandedSources.has(item.question_id) && item.sources.length > 0}
							<div class="mt-4 border-t pt-4">
								<h4 class="text-sm font-medium text-gray-700 mb-2">根拠</h4>
								<div class="space-y-2">
									{#each item.sources as source}
										<div class="bg-gray-50 rounded p-3 text-sm">
											<span class="font-medium">
												{source.type === 'pageindex' ? 'ドキュメント' : 'ナレッジベース'}:
											</span>
											{#if source.document_name}
												<span class="text-gray-600">
													{source.document_name}
													{#if source.page_number}(p.{source.page_number}){/if}
												</span>
											{/if}
											{#if source.snippet}
												<p class="mt-1 text-gray-600 italic">"{source.snippet}"</p>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/each}
			</div>
		{/if}
	{/if}
</div>
