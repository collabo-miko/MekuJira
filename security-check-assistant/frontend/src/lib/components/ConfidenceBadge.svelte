<script lang="ts">
	export let score: number;
	export let level: 'high' | 'medium' | 'low' | null = null;

	$: computedLevel = level || (score >= 0.85 ? 'high' : score >= 0.7 ? 'medium' : 'low');
	$: percentage = Math.round(score * 100);
</script>

<span
	class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
		{computedLevel === 'high'
		? 'bg-green-100 text-green-800'
		: computedLevel === 'medium'
			? 'bg-yellow-100 text-yellow-800'
			: 'bg-red-100 text-red-800'}"
>
	{percentage}%
</span>
