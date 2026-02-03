<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getReport, getExportUrl, type Report } from '$lib/api/client';

	let report: Report | null = null;
	let loading = true;
	let error: string | null = null;

	$: sessionId = $page.params.session_id;

	onMount(async () => {
		try {
			report = await getReport(sessionId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'エラーが発生しました';
		} finally {
			loading = false;
		}
	});

	function downloadExcel() {
		window.location.href = getExportUrl(sessionId);
	}
</script>

<svelte:head>
	<title>レポート - Security Check Assistant</title>
</svelte:head>

<div class="px-4 sm:px-0 max-w-4xl mx-auto">
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
			<p class="mt-2 text-gray-600">読み込み中...</p>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else if report}
		<div class="flex justify-between items-start mb-6">
			<div>
				<h1 class="text-2xl font-bold text-gray-900">レポート</h1>
				<p class="text-gray-500">{report.summary.filename}</p>
			</div>
			<div class="flex space-x-4">
				<a
					href="/review/{sessionId}"
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
				>
					レビューに戻る
				</a>
				<button
					class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
					on:click={downloadExcel}
				>
					Excelダウンロード
				</button>
			</div>
		</div>

		<!-- Summary Stats -->
		<div class="bg-white shadow rounded-lg p-6 mb-6">
			<h2 class="text-lg font-medium text-gray-900 mb-4">サマリー</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="bg-gray-50 rounded-lg p-4 text-center">
					<p class="text-3xl font-bold text-gray-900">{report.summary.total_questions}</p>
					<p class="text-sm text-gray-500">合計質問数</p>
				</div>
				<div class="bg-green-50 rounded-lg p-4 text-center">
					<p class="text-3xl font-bold text-green-600">{report.summary.answered_count}</p>
					<p class="text-sm text-gray-500">回答済み</p>
				</div>
				<div class="bg-blue-50 rounded-lg p-4 text-center">
					<p class="text-3xl font-bold text-blue-600">
						{report.summary.approved_count + report.summary.modified_count}
					</p>
					<p class="text-sm text-gray-500">承認済み</p>
				</div>
				<div class="bg-yellow-50 rounded-lg p-4 text-center">
					<p class="text-3xl font-bold text-yellow-600">{report.summary.pending_count}</p>
					<p class="text-sm text-gray-500">未承認</p>
				</div>
			</div>
		</div>

		<!-- Confidence Distribution -->
		<div class="bg-white shadow rounded-lg p-6 mb-6">
			<h2 class="text-lg font-medium text-gray-900 mb-4">確信度分布</h2>
			<div class="space-y-3">
				<div class="flex items-center">
					<span class="w-24 text-sm text-gray-600">高 (85%以上)</span>
					<div class="flex-1 h-4 bg-gray-100 rounded overflow-hidden">
						<div
							class="h-full bg-green-500"
							style="width: {(report.summary.high_confidence_count /
								report.summary.total_questions) *
								100}%"
						></div>
					</div>
					<span class="w-16 text-right text-sm text-gray-600">
						{report.summary.high_confidence_count}件
					</span>
				</div>
				<div class="flex items-center">
					<span class="w-24 text-sm text-gray-600">中 (70-85%)</span>
					<div class="flex-1 h-4 bg-gray-100 rounded overflow-hidden">
						<div
							class="h-full bg-yellow-500"
							style="width: {(report.summary.medium_confidence_count /
								report.summary.total_questions) *
								100}%"
						></div>
					</div>
					<span class="w-16 text-right text-sm text-gray-600">
						{report.summary.medium_confidence_count}件
					</span>
				</div>
				<div class="flex items-center">
					<span class="w-24 text-sm text-gray-600">低 (70%未満)</span>
					<div class="flex-1 h-4 bg-gray-100 rounded overflow-hidden">
						<div
							class="h-full bg-red-500"
							style="width: {(report.summary.low_confidence_count /
								report.summary.total_questions) *
								100}%"
						></div>
					</div>
					<span class="w-16 text-right text-sm text-gray-600">
						{report.summary.low_confidence_count}件
					</span>
				</div>
			</div>
		</div>

		<!-- Difficult Questions -->
		{#if report.difficult_questions.length > 0}
			<div class="bg-white shadow rounded-lg p-6 mb-6">
				<h2 class="text-lg font-medium text-gray-900 mb-4">
					回答に困った質問 ({report.difficult_questions.length}件)
				</h2>
				<div class="space-y-3">
					{#each report.difficult_questions as dq}
						<div class="border border-red-200 rounded-lg p-4 bg-red-50">
							<div class="flex justify-between items-start">
								<p class="text-gray-900">#{dq.row_number}: {dq.question_text}</p>
								<span class="text-sm text-red-600 whitespace-nowrap ml-4">
									{Math.round(dq.confidence_score * 100)}%
								</span>
							</div>
							<p class="text-sm text-red-600 mt-1">{dq.reason}</p>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Knowledge Base -->
		<div class="bg-white shadow rounded-lg p-6">
			<h2 class="text-lg font-medium text-gray-900 mb-4">ナレッジベース</h2>
			<p class="text-gray-600">
				現在 <span class="font-medium">{report.knowledge_count}</span> 件の回答がナレッジベースに蓄積されています。
			</p>
			<p class="text-sm text-gray-500 mt-2">
				承認された回答はナレッジベースに保存され、将来の回答生成の精度向上に活用されます。
			</p>
		</div>
	{/if}
</div>
