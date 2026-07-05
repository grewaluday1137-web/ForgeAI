import { create } from "zustand"
import { persist } from "zustand/middleware"
import { Project } from "@/services/projects"

interface ProjectState {
  activeProjectId: string | null
  setActiveProject: (id: string) => void
  clearActiveProject: () => void
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      activeProjectId: null,
      setActiveProject: (id) => set({ activeProjectId: id }),
      clearActiveProject: () => set({ activeProjectId: null }),
    }),
    {
      name: "forgeai-project-storage",
    }
  )
)
