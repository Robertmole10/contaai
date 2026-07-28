import { Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
};

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: PageHeaderProps) {
  return (
    <section className="ca-page-header">
      <div>
        <span className="ca-eyebrow">
          <Sparkles size={14} />
          {eyebrow}
        </span>

        <h1>{title}</h1>
        <p>{description}</p>
      </div>

      {actions && <div className="ca-page-actions">{actions}</div>}
    </section>
  );
}
