import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { fetchFolders } from '@/features/folders/foldersSlice'
import { fetchDocuments } from '@/features/documents/documentsSlice'
import { Folder, FileText } from 'lucide-react'

const Sidebar = () => {
  const dispatch = useAppDispatch()
  const { folders } = useAppSelector((state) => state.folders)
  const { documents } = useAppSelector((state) => state.documents)

  useEffect(() => {
    dispatch(fetchFolders())
    dispatch(fetchDocuments())
  }, [dispatch])

  return (
    <aside className="w-64 bg-white border-r min-h-[calc(100vh-4rem)]">
      <div className="p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
          文件夹
        </h3>
        <div className="space-y-1">
          {folders.map((folder) => (
            <div
              key={folder.id}
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 cursor-pointer"
            >
              <Folder className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">{folder.name}</span>
            </div>
          ))}
        </div>

        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 mt-6">
          最近文档
        </h3>
        <div className="space-y-1">
          {documents.slice(0, 5).map((doc) => (
            <div
              key={doc.id}
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 cursor-pointer"
            >
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700 truncate">{doc.name}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
