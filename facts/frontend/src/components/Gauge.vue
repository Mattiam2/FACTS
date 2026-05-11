<template>
  <svg viewBox="0 0 120 70" width="120" height="70">
    <!-- Background arc -->
    <path
      d="M 10 65 A 50 50 0 0 1 110 65"
      fill="none"
      stroke="rgba(255,255,255,0.1)"
      stroke-width="10"
      stroke-linecap="round"
    />
    <!-- Value arc -->
    <path
      d="M 10 65 A 50 50 0 0 1 110 65"
      fill="none"
      :stroke="color"
      stroke-width="10"
      stroke-linecap="round"
      :stroke-dasharray="dashArray"
      stroke-dashoffset="0"
    />
    <!-- Label -->
    <text x="60" y="60" text-anchor="middle" font-size="18" font-weight="bold" :fill="color">
      {{ value }}
    </text>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ value: Number, max: { default: 5 } })

const arcLength = 157 // half circumference of r=50

const dashArray = computed(() => {
  const filled = (props.value / props.max) * arcLength
  return `${filled} ${arcLength}`
})

const color = computed(() => {
  if (props.value <= 2) return '#ff5252'
  if (props.value <= 3) return '#ffb300'
  return '#00e5b4'
})
</script>