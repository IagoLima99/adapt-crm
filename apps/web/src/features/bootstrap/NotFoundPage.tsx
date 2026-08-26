import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <main className="bootstrap-shell">
      <p className="eyebrow">404</p>
      <h1>Página não encontrada</h1>
      <Link to="/">Voltar ao início</Link>
    </main>
  );
}
