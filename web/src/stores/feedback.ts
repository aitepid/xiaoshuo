import { ref } from 'vue'
import { defineStore } from 'pinia'

type ToastType = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  type: ToastType
  title: string
  message?: string
}

interface ModalState {
  open: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  onConfirm?: () => void
}

let seed = 1

export const useFeedbackStore = defineStore('feedback', () => {
  const toasts = ref<ToastItem[]>([])
  const modal = ref<ModalState>({
    open: false,
    title: '',
    message: '',
    confirmText: '确认',
    cancelText: '取消',
  })

  function pushToast(type: ToastType, title: string, message = ''): void {
    const id = seed++
    toasts.value.push({ id, type, title, message })

    window.setTimeout(() => {
      removeToast(id)
    }, 2600)
  }

  function removeToast(id: number): void {
    toasts.value = toasts.value.filter((item) => item.id !== id)
  }

  function openModal(payload: Omit<ModalState, 'open'>): void {
    modal.value = { open: true, ...payload }
  }

  function closeModal(): void {
    modal.value = {
      open: false,
      title: '',
      message: '',
      confirmText: '确认',
      cancelText: '取消',
    }
  }

  function confirmModal(): void {
    modal.value.onConfirm?.()
    closeModal()
  }

  return {
    toasts,
    modal,
    pushToast,
    removeToast,
    openModal,
    closeModal,
    confirmModal,
  }
})
