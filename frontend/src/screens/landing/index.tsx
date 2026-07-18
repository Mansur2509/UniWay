import { FeatureGrid } from "./feature-grid";
import { FinalCta } from "./final-cta";
import { HeroSection } from "./hero-section";
import { HowItWorks } from "./how-it-works";
import { LandingFooter } from "./landing-footer";
import { LandingHeader } from "./landing-header";
import { LanguagesSection } from "./languages-section";
import { OrganizerSection } from "./organizer-section";
import { ProductShowcase } from "./product-showcase";
import { TrustSection } from "./trust-section";
import { UniversityMarquee } from "./university-marquee";

export function LandingScreen() {
  return (
    <div className="bg-background">
      <LandingHeader />
      <HeroSection />
      <TrustSection />
      <UniversityMarquee />
      <FeatureGrid />
      <HowItWorks />
      <OrganizerSection />
      <ProductShowcase />
      <LanguagesSection />
      <FinalCta />
      <LandingFooter />
    </div>
  );
}
