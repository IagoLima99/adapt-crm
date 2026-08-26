import { Route, Routes } from "react-router";

import { BootstrapPage } from "../features/bootstrap/BootstrapPage";
import { NotFoundPage } from "../features/bootstrap/NotFoundPage";

export function App() {
  return (
    <Routes>
      <Route index element={<BootstrapPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
