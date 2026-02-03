<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let accept = '.xlsx,.xls';
	export let label = 'ファイルをドラッグ＆ドロップまたはクリックして選択';
	export let disabled = false;

	const dispatch = createEventDispatcher<{ file: File }>();

	let isDragging = false;
	let fileInput: HTMLInputElement;

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		if (!disabled) isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		if (disabled) return;

		const files = e.dataTransfer?.files;
		if (files && files.length > 0) {
			dispatch('file', files[0]);
		}
	}

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files && input.files.length > 0) {
			dispatch('file', input.files[0]);
		}
	}

	function openFilePicker() {
		if (!disabled) fileInput.click();
	}
</script>

<div
	class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
		{isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
		{disabled ? 'opacity-50 cursor-not-allowed' : ''}"
	on:dragover={handleDragOver}
	on:dragleave={handleDragLeave}
	on:drop={handleDrop}
	on:click={openFilePicker}
	on:keydown={(e) => e.key === 'Enter' && openFilePicker()}
	role="button"
	tabindex="0"
>
	<input
		type="file"
		{accept}
		class="hidden"
		bind:this={fileInput}
		on:change={handleFileSelect}
		{disabled}
	/>
	<svg
		class="mx-auto h-12 w-12 text-gray-400"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
		/>
	</svg>
	<p class="mt-2 text-sm text-gray-600">{label}</p>
	<p class="mt-1 text-xs text-gray-500">対応形式: {accept}</p>
</div>
