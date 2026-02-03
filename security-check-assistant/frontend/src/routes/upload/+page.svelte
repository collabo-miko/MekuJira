<script lang="ts">
	import { goto } from '$app/navigation';
	import { uploadExcel, generateAnswers } from '$lib/api/client';
	import FileUpload from '$lib/components/FileUpload.svelte';

	let uploading = false;
	let error: string | null = null;
	let vendorName = '';
	let confidenceThreshold = 0.7;

	const thresholdOptions = [
		{ value: 0.95, label: '厳格 (95%)' },
		{ value: 0.85, label: 'やや厳格 (85%)' },
		{ value: 0.7, label: '標準 (70%)' }
	];

	async function handleFileUpload(event: CustomEvent<File>) {
		const file = event.detail;
		if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
			error = 'Excelファイル（.xlsx, .xls）のみアップロード可能です';
			return;
		}

		try {
			uploading = true;
			error = null;

			// Upload and create session
			const session = await uploadExcel(file, vendorName || undefined, confidenceThreshold);

			// Wait a bit for format detection to complete
			await new Promise((resolve) => setTimeout(resolve, 2000));

			// Start answer generation
			await generateAnswers(session.id, confidenceThreshold);

			// Navigate to review page
			goto(`/review/${session.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'アップロードに失敗しました';
			uploading = false;
		}
	}
</script>

<svelte:head>
	<title>Excelアップロード - Security Check Assistant</title>
</svelte:head>

<div class="px-4 sm:px-0 max-w-2xl mx-auto">
	<h1 class="text-2xl font-bold text-gray-900 mb-6">セキュリティチェックシートをアップロード</h1>

	<div class="bg-white shadow rounded-lg p-6">
		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
				<p class="text-red-800">{error}</p>
			</div>
		{/if}

		<div class="space-y-6">
			<div>
				<label for="vendorName" class="block text-sm font-medium text-gray-700 mb-1">
					ベンダー名（任意）
				</label>
				<input
					type="text"
					id="vendorName"
					bind:value={vendorName}
					class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
					placeholder="例: 株式会社ABC"
					disabled={uploading}
				/>
			</div>

			<div>
				<label for="confidenceThreshold" class="block text-sm font-medium text-gray-700 mb-1">
					確信度閾値
				</label>
				<select
					id="confidenceThreshold"
					bind:value={confidenceThreshold}
					class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
					disabled={uploading}
				>
					{#each thresholdOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
				<p class="mt-1 text-sm text-gray-500">
					閾値以上の確信度を持つ回答のみが自動的にセットされます
				</p>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Excelファイル
				</label>
				<FileUpload
					accept=".xlsx,.xls"
					label="セキュリティチェックシート（Excel）をドラッグ＆ドロップ"
					disabled={uploading}
					on:file={handleFileUpload}
				/>
			</div>

			{#if uploading}
				<div class="text-center py-4">
					<div
						class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
					></div>
					<p class="mt-2 text-gray-600">処理中... フォーマット検出と回答生成を行っています</p>
				</div>
			{/if}
		</div>
	</div>

	<div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
		<h3 class="font-medium text-blue-900 mb-2">処理の流れ</h3>
		<ol class="list-decimal list-inside text-sm text-blue-800 space-y-1">
			<li>Excelファイルをアップロード</li>
			<li>シート構造を自動検出（質問列・回答列を特定）</li>
			<li>質問を抽出して一括回答生成</li>
			<li>レビュー画面で確認・修正</li>
			<li>確定後、記入済みExcelをダウンロード</li>
		</ol>
	</div>
</div>
