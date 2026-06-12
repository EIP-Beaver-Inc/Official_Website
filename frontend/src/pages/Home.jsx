import Hero from '@/components/home/Hero';
import PipelineSection from '@/components/home/PipelineSection';
import DefectsSection from '@/components/home/DefectsSection';
import FinalCTA from '@/components/home/FinalCTA';

export default function Home() {
    return (
        <div data-testid="home-page">
            <Hero />
            <PipelineSection />
            <DefectsSection />
            <FinalCTA />
        </div>
    );
}
