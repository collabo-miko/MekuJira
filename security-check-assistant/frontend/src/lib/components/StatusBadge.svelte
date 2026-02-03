<script lang="ts">
	export let status: string;

	const statusStyles: Record<string, string> = {
		uploaded: 'bg-gray-100 text-gray-800',
		detecting: 'bg-blue-100 text-blue-800',
		detected: 'bg-blue-100 text-blue-800',
		generating: 'bg-yellow-100 text-yellow-800',
		generated: 'bg-green-100 text-green-800',
		reviewing: 'bg-purple-100 text-purple-800',
		finalized: 'bg-green-100 text-green-800',
		error: 'bg-red-100 text-red-800',
		pending: 'bg-gray-100 text-gray-800',
		approved: 'bg-green-100 text-green-800',
		modified: 'bg-blue-100 text-blue-800',
		rejected: 'bg-red-100 text-red-800',
		uploading: 'bg-gray-100 text-gray-800',
		indexing: 'bg-yellow-100 text-yellow-800',
		indexed: 'bg-green-100 text-green-800'
	};

	const statusLabels: Record<string, string> = {
		uploaded: 'アップロード済み',
		detecting: '検出中',
		detected: '検出完了',
		generating: '生成中',
		generated: '生成完了',
		reviewing: 'レビュー中',
		finalized: '確定済み',
		error: 'エラー',
		pending: '未承認',
		approved: '承認済み',
		modified: '修正済み',
		rejected: '却下',
		uploading: 'アップロード中',
		indexing: 'インデックス中',
		indexed: 'インデックス済み'
	};

	$: style = statusStyles[status] || 'bg-gray-100 text-gray-800';
	$: label = statusLabels[status] || status;
</script>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {style}">
	{label}
</span>
