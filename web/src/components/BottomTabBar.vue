<template>
  <nav class="fixed inset-x-0 bottom-3 z-20 mx-auto w-[min(96vw,560px)] rounded-2xl border border-black/10 bg-white/85 px-2 py-2 shadow-lg backdrop-blur md:hidden dark:border-white/15 dark:bg-slate-900/85">
    <ul class="grid grid-cols-4 gap-1 text-xs">
      <li>
        <RouterLink class="tab-item" to="/">首页</RouterLink>
      </li>
      <li>
        <RouterLink class="tab-item" to="/bookshelf">书架</RouterLink>
      </li>
      <li>
        <RouterLink class="tab-item" to="/creator">创作</RouterLink>
      </li>
      <li>
        <RouterLink class="tab-item" to="/auth/login">我的</RouterLink>
      </li>
    </ul>
  </nav>
</template>
