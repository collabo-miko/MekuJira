<script lang="ts">
	import { goto } from '$app/navigation';
	import { uploadExcel, generateAnswers } from '$lib/api/client';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import ExcelPreview from '$lib/components/ExcelPreview.svelte';

	let uploading = false;
	let error: string | null = null;
	let vendorName = '';
	let confidenceThreshold = 0.7;
	let selectedFile: File | null = null;
	let showPreview = false;

	const thresholdOptions = [
		{ value: 0.95, label: '厳格 (95%)' },
		{ value: 0.85, label: 'やや厳格 (85%)' },
		{ value: 0.7, label: '標準 (70%)' }
	];

	function handleFileSelect(event: CustomEvent<File>) {
		const file = event.detail;
		if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
			error = 'Excelファイル（.xlsx, .xls）のみアップロード可能です';
			selectedFile = null;
			showPreview = false;
			return;
		}

		error = null;
		selectedFile = file;
		showPreview = true;
	}

	function clearFile() {
		selectedFile = null;
		showPreview = false;
		error = null;
	}

	async function handleUpload() {
		if (!selectedFile) {
			error = 'ファイルを選択してください';
			return;
		}

		try {
			uploading = true;
			error = null;

			// Upload and create session
			const session = await uploadExcel(selectedFile, vendorName || undefined, confidenceThreshold);

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

<div class="px-4 sm:px-0 max-w-4xl mx-auto">
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

			{#if !showPreview}
				<div>
					<span class="block text-sm font-medium text-gray-700 mb-2">Excelファイル</span>
					<FileUpload
						accept=".xlsx,.xls"
						label="セキュリティチェックシート（Excel）をドラッグ＆ドロップ"
						disabled={uploading}
						on:file={handleFileSelect}
					/>
				</div>
			{:else if selectedFile}
				<div>
					<div class="flex items-center justify-between mb-2">
						<span class="block text-sm font-medium text-gray-700">
							ファイルプレビュー: {selectedFile.name}
						</span>
						<button
							type="button"
							class="text-sm text-gray-500 hover:text-gray-700"
							on:click={clearFile}
							disabled={uploading}
						>
							✕ 別のファイルを選択
						</button>
					</div>
					<ExcelPreview file={selectedFile} maxRows={50} />
				</div>

				<div class="flex gap-4">
					<button
						type="button"
						class="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed font-medium"
						on:click={handleUpload}
						disabled={uploading}
					>
						{#if uploading}
							<span class="inline-flex items-center">
								<span
									class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
								></span>
								処理中...
							</span>
						{:else}
							アップロードして回答生成を開始
						{/if}
					</button>
				</div>
			{/if}

			{#if uploading}
				<div class="text-center py-4">
					<p class="text-gray-600">フォーマット検出と回答生成を行っています...</p>
				</div>
			{/if}
		</div>
	</div>

	<div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
		<h3 class="font-medium text-blue-900 mb-2">処理の流れ</h3>
		<ol class="list-decimal list-inside text-sm text-blue-800 space-y-1">
			<li>Excelファイルを選択してプレビューを確認</li>
			<li>「アップロードして回答生成を開始」をクリック</li>
			<li>シート構造を自動検出（質問列・回答列を特定）</li>
			<li>質問を抽出して一括回答生成</li>
			<li>レビュー画面で確認・修正</li>
			<li>確定後、記入済みExcelをダウンロード</li>
		</ol>
	</div>
</div>
