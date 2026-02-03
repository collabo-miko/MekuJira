<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getDocuments,
		uploadDocument,
		deleteDocument,
		type Document
	} from '$lib/api/client';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';

	let documents: Document[] = [];
	let loading = true;
	let uploading = false;
	let error: string | null = null;

	onMount(async () => {
		await loadDocuments();
	});

	async function loadDocuments() {
		try {
			loading = true;
			documents = await getDocuments();
		} catch (e) {
			error = e instanceof Error ? e.message : 'エラーが発生しました';
		} finally {
			loading = false;
		}
	}

	async function handleFileUpload(event: CustomEvent<File>) {
		const file = event.detail;
		if (!file.name.endsWith('.pdf')) {
			error = 'PDFファイルのみアップロード可能です';
			return;
		}

		try {
			uploading = true;
			error = null;
			await uploadDocument(file);
			await loadDocuments();
		} catch (e) {
			error = e instanceof Error ? e.message : 'アップロードに失敗しました';
		} finally {
			uploading = false;
		}
	}

	async function handleDelete(docId: string) {
		if (!confirm('このドキュメントを削除しますか？')) return;

		try {
			await deleteDocument(docId);
			await loadDocuments();
		} catch (e) {
			error = e instanceof Error ? e.message : '削除に失敗しました';
		}
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return '-';
		return new Date(dateStr).toLocaleString('ja-JP');
	}
</script>

<svelte:head>
	<title>ドキュメント管理 - Security Check Assistant</title>
</svelte:head>

<div class="px-4 sm:px-0">
	<h1 class="text-2xl font-bold text-gray-900 mb-6">ドキュメント管理</h1>

	<div class="bg-white shadow rounded-lg p-6 mb-6">
		<h2 class="text-lg font-medium text-gray-900 mb-4">PDFドキュメントをアップロード</h2>
		<div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
			<p class="text-sm text-yellow-800">
				<strong>注意:</strong> アップロードされたPDFはPageIndex
				APIに送信され、インデックス化されます。
			</p>
		</div>
		<FileUpload accept=".pdf" label="PDFをドラッグ＆ドロップ" disabled={uploading} on:file={handleFileUpload} />
		{#if uploading}
			<p class="mt-2 text-sm text-gray-600">アップロード中...</p>
		{/if}
	</div>

	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
			<p class="text-red-800">{error}</p>
		</div>
	{/if}

	<div class="bg-white shadow rounded-lg">
		<div class="px-4 py-5 sm:px-6 border-b">
			<h2 class="text-lg font-medium text-gray-900">登録済みドキュメント</h2>
		</div>
		{#if loading}
			<div class="px-4 py-8 text-center">
				<div
					class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"
				></div>
			</div>
		{:else if documents.length === 0}
			<div class="px-4 py-8 text-center text-gray-500">
				ドキュメントがありません。PDFファイルをアップロードしてください。
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
								ファイル名
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
								ページ数
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
								ステータス
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
								インデックス日時
							</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
								操作
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each documents as doc}
							<tr>
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
									{doc.filename}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{doc.page_count ?? '-'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<StatusBadge status={doc.status} />
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDate(doc.indexed_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm">
									<button
										class="text-red-600 hover:text-red-900"
										on:click={() => handleDelete(doc.id)}
									>
										削除
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
