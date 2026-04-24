export interface Folder {
  id: string
  name: string
  parentId?: string
  createTime: string
  children?: Folder[]
}

export interface FoldersState {
  folders: Folder[]
  currentFolder: Folder | null
  isLoading: boolean
  error: string | null
}
