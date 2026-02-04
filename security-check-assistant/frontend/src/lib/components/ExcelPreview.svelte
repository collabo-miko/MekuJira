<script lang="ts">
	import { onMount } from 'svelte';
	import * as XLSX from 'xlsx';

	export let file: File | null = null;
	export let maxRows: number = 100;
	export let highlightColumns: { question?: number; answer?: number } = {};

	let workbook: XLSX.WorkBook | null = null;
	let sheetNames: string[] = [];
	let activeSheet: string = '';
	let sheetData: (string | number | null)[][] = [];
	let loading = false;
	let error: string | null = null;

	$: if (file) {
		loadExcelFile(file);
	}

	async function loadExcelFile(f: File) {
		loading = true;
		error = null;
		try {
			const arrayBuffer = await f.arrayBuffer();
			workbook = XLSX.read(arrayBuffer, { type: 'array' });
			sheetNames = workbook.SheetNames;
			if (sheetNames.length > 0) {
				activeSheet = sheetNames[0];
				loadSheet(activeSheet);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Excelファイルの読み込みに失敗しました';
			workbook = null;
			sheetNames = [];
			sheetData = [];
		} finally {
			loading = false;
		}
	}

	function loadSheet(name: string) {
		if (!workbook) return;
		const sheet = workbook.Sheets[name];
		if (!sheet) return;

		const json = XLSX.utils.sheet_to_json<(string | number | null)[]>(sheet, {
			header: 1,
			defval: null
		});

		// Limit rows for performance
		sheetData = json.slice(0, maxRows);
		activeSheet = name;
	}

	function selectSheet(name: string) {
		loadSheet(name);
	}

	function getColumnLetter(index: number): string {
		let letter = '';
		while (index >= 0) {
			letter = String.fromCharCode((index % 26) + 65) + letter;
			index = Math.floor(index / 26) - 1;
		}
		return letter;
	}

	function isHighlightedColumn(colIndex: number): 'question' | 'answer' | null {
		if (highlightColumns.question === colIndex) return 'question';
		if (highlightColumns.answer === colIndex) return 'answer';
		return null;
	}

	function getCellClass(colIndex: number): string {
		const highlight = isHighlightedColumn(colIndex);
		if (highlight === 'question') return 'bg-blue-50';
		if (highlight === 'answer') return 'bg-green-50';
		return '';
	}

	function getHeaderClass(colIndex: number): string {
		const highlight = isHighlightedColumn(colIndex);
		if (highlight === 'question') return 'bg-blue-100 text-blue-800';
		if (highlight === 'answer') return 'bg-green-100 text-green-800';
		return 'bg-gray-100';
	}

	// Get max column count from data
	$: maxColumns = sheetData.reduce((max, row) => Math.max(max, row?.length || 0), 0);
</script>

<div class="excel-preview">
	{#if loading}
		<div class="flex items-center justify-center py-8">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-2 text-gray-600">読み込み中...</span>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else if sheetNames.length > 0}
		<!-- Sheet tabs -->
		<div class="flex border-b border-gray-200 mb-2 overflow-x-auto">
			{#each sheetNames as name}
				<button
					type="button"
					class="px-4 py-2 text-sm font-medium whitespace-nowrap {activeSheet === name
						? 'border-b-2 border-blue-500 text-blue-600'
						: 'text-gray-500 hover:text-gray-700'}"
					on:click={() => selectSheet(name)}
				>
					{name}
				</button>
			{/each}
		</div>

		<!-- Legend for highlights -->
		{#if highlightColumns.question !== undefined || highlightColumns.answer !== undefined}
			<div class="flex gap-4 mb-2 text-sm">
				{#if highlightColumns.question !== undefined}
					<span class="flex items-center">
						<span class="w-4 h-4 bg-blue-100 border border-blue-300 rounded mr-1"></span>
						質問列 ({getColumnLetter(highlightColumns.question)})
					</span>
				{/if}
				{#if highlightColumns.answer !== undefined}
					<span class="flex items-center">
						<span class="w-4 h-4 bg-green-100 border border-green-300 rounded mr-1"></span>
						回答列 ({getColumnLetter(highlightColumns.answer)})
					</span>
				{/if}
			</div>
		{/if}

		<!-- Table container -->
		<div class="overflow-auto max-h-96 border border-gray-200 rounded">
			<table class="min-w-full text-sm">
				<!-- Column headers (A, B, C...) -->
				<thead class="sticky top-0 z-10">
					<tr>
						<th class="bg-gray-200 border-r border-b border-gray-300 px-2 py-1 text-center w-12">
							#
						</th>
						{#each Array(maxColumns) as _, i}
							<th
								class="border-r border-b border-gray-300 px-2 py-1 text-center min-w-[80px] {getHeaderClass(
									i
								)}"
							>
								{getColumnLetter(i)}
							</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each sheetData as row, rowIndex}
						<tr class="hover:bg-gray-50">
							<!-- Row number -->
							<td
								class="bg-gray-100 border-r border-b border-gray-200 px-2 py-1 text-center text-gray-500 font-mono"
							>
								{rowIndex + 1}
							</td>
							<!-- Cells -->
							{#each Array(maxColumns) as _, colIndex}
								<td
									class="border-r border-b border-gray-200 px-2 py-1 {getCellClass(colIndex)}"
									title={row?.[colIndex]?.toString() || ''}
								>
									<div class="max-w-xs truncate">
										{row?.[colIndex] ?? ''}
									</div>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Row count info -->
		<div class="mt-2 text-sm text-gray-500">
			{#if sheetData.length >= maxRows}
				最初の {maxRows} 行を表示しています
			{:else}
				{sheetData.length} 行
			{/if}
		</div>
	{:else}
		<div class="text-gray-500 text-center py-4">
			Excelファイルを選択してください
		</div>
	{/if}
</div>

<style>
	.excel-preview {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}
</style>
