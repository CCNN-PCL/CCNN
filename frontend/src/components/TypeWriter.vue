<template>
  <span v-html="display"/>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'
const emit = defineEmits(['done'])

const props = defineProps({
  text: { type: String, required: true },   // 最终要显示的完整 HTML
  speed: { type: Number, default: 30 }      // 每字间隔 ms
})

const display = ref('')
let idx = 0
let timer = null

const type = () => {
  if (idx >= props.text.length) {
    emit('done')   // ⬅️ 动画结束
    return
    }
  // 把下一个字符追加进去
  display.value += props.text[idx]
  idx++
  timer = setTimeout(type, props.speed)
}

watch(
  () => props.text,
  (val) => {
    display.value = ''
    idx = 0
    clearTimeout(timer)
    if (val) type()
  },
  { immediate: true }
)

onUnmounted(() => clearTimeout(timer))
</script>