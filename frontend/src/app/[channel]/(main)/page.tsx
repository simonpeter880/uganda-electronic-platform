import HeroCarousel from "@/components/uganda/HeroCarousel";
import FlashDeals from "@/components/uganda/FlashDeals";
import CategoryGrid from "@/components/uganda/CategoryGrid";
import ProductCard from "@/components/uganda/ProductCard";
import TrustBadges from "@/components/uganda/TrustBadges";
import ReviewsCarousel from "@/components/uganda/ReviewsCarousel";
import {
	mockHeroSlides,
	mockFlashDeals,
	mockFeaturedProducts,
	mockCustomerReviews,
} from "@/lib/mock-data";

export const metadata = {
	title: "Uganda Electronics - Premium Phones, Laptops & Gaming | Kampala",
	description:
		"Uganda's #1 electronics shop. iPhones, Samsung, MacBooks, Gaming PCs. MTN & Airtel Money. Free delivery to all districts. Shop genuine products with warranty!",
};

export default async function HomePage(props: { params: Promise<{ channel: string }> }) {
	const params = await props.params;
	const flashDealEndsAt = new Date();
	flashDealEndsAt.setHours(flashDealEndsAt.getHours() + 24);

	return (
		<div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
			<div className="container mx-auto px-4 py-4 space-y-8">
				<HeroCarousel slides={mockHeroSlides} />
				<CategoryGrid />
				<FlashDeals products={mockFlashDeals} endsAt={flashDealEndsAt} />
				<section>
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-2xl font-bold text-gray-900">Featured Products</h2>
						<a href="/products" className="text-primary-500 hover:text-primary-600 font-semibold text-sm flex items-center gap-1">
							View All
							<span>→</span>
						</a>
					</div>
					<div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-3">
						{mockFeaturedProducts.map((product) => (
							<ProductCard
								key={product.id}
								{...product}
								installmentPrice={Math.round(product.price / 3)}
							/>
						))}
					</div>
				</section>
				<TrustBadges />
				<ReviewsCarousel reviews={mockCustomerReviews} />
			</div>
		</div>
	);
}
