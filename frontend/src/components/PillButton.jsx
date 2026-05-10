import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function PillButton({
    children,
    onClick,
    to,
    href,
    variant = 'primary',
    size = 'md',
    icon = true,
    type = 'button',
    className = '',
    testId,
}) {
    const sizes = {
        sm: 'h-10 px-4 text-sm',
        md: 'h-11 px-5 text-sm',
        lg: 'h-12 sm:h-[54px] px-6 sm:px-7 text-sm sm:text-base',
    };
    const variants = {
        primary:
            'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(14_66%_38%)] shadow-[0_8px_24px_rgba(168,65,42,0.18)]',
        outline:
            'bg-transparent border border-black/15 text-[hsl(var(--foreground))] hover:bg-[hsl(var(--card))]',
        ghost:
            'bg-[hsl(var(--card))] border border-black/5 text-[hsl(var(--foreground))] hover:bg-[hsl(38_45%_94%)]',
    };
    const cls = `inline-flex items-center justify-center rounded-full font-medium transition-colors duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--background))] ${sizes[size]} ${variants[variant]} ${className}`;

    const content = (
        <>
            <span>{children}</span>
            {icon && <ArrowRight className="ml-2 h-4 w-4" />}
        </>
    );

    if (to) {
        return (
            <Link to={to} className={cls} data-testid={testId}>
                {content}
            </Link>
        );
    }
    if (href) {
        return (
            <a href={href} className={cls} data-testid={testId}>
                {content}
            </a>
        );
    }
    return (
        <button type={type} onClick={onClick} className={cls} data-testid={testId}>
            {content}
        </button>
    );
}
