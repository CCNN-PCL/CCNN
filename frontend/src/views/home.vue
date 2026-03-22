<template>
  <div> </div>
</template>

<script>
import { ref, computed, defineComponent, watch,onMounted } from 'vue';


export default defineComponent({
  name: 'home',
  setup() {
    onMounted(() => {
        // window.location.href = `${process.env.USER_AGENT}/login`
        window.location.href = '/login'

    })
    return {
        
    }
  }
});
</script>

<style lang="scss" scoped>
</style>