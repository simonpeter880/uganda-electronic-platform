"use client";

import { useState, useMemo } from "react";
import { SlidersHorizontal, Grid3x3, List, ChevronRight } from "lucide-react";
import ProductCard from "@/components/uganda/ProductCard";
import FilterSidebar, { Filters } from "@/components/uganda/FilterSidebar";
import { mockFeaturedProducts, mockFlashDeals } from "@/lib/mock-data";

// Combine all products for listing
const allProducts = [...mockFlashDeals, ...mockFeaturedProducts].map((product) => ({
	...product,
	installmentPrice: Math.round(product.price / 3),
}));

type SortOption = "popular" | "price-low" | "price-high" | "newest" | "rating";

interface SortConfig {
	value: SortOption;
	label: string;
}

const sortOptions: SortConfig[] = [
	{ value: "popular", label: "Most Popular" },
	{ value: "price-low", label: "Price: Low to High" },
	{ value: "price-high", label: "Price: High to Low" },
	{ value: "newest", label: "Newest Arrivals" },
	{ value: "rating", label: "Highest Rated" },
];

export default function ProductsPage() {
	const [filters, setFilters] = useState<Filters>({
		priceRange: [0, 10000000],
		brands: [],
		conditions: [],
		storage: [],
		features: [],
	});
	const [sortBy, setSortBy] = useState<SortOption>("popular");
	const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
	const [isFilterOpen, setIsFilterOpen] = useState(false);

	// Apply filters and sorting
	const filteredAndSortedProducts = useMemo(() => {
		let result = [...allProducts];

		// Apply price range filter
		result = result.filter(
			(p) => p.price >= filters.priceRange[0] && p.price <= filters.priceRange[1]
		);

		// Apply brand filter
		if (filters.brands.length > 0) {
			result = result.filter((p) => {
				// Extract brand from product name (simplified)
				const nameLower = p.name.toLowerCase();
				return filters.brands.some((brand) => nameLower.includes(brand.toLowerCase()));
			});
		}

		// Apply storage filter (if product has storage in name)
		if (filters.storage.length > 0) {
			result = result.filter((p) => {
				const nameLower = p.name.toLowerCase();
				return filters.storage.some((storage) => nameLower.includes(storage.toLowerCase()));
			});
		}

		// Apply sorting
		switch (sortBy) {
			case "price-low":
				result.sort((a, b) => a.price - b.price);
				break;
			case "price-high":
				result.sort((a, b) => b.price - a.price);
				break;
			case "rating":
				result.sort((a, b) => (b.rating || 0) - (a.rating || 0));
				break;
			case "newest":
				// Simulate newest by reversing (in real app, use createdAt)
				result.reverse();
				break;
			case "popular":
			default:
				// Keep default order or sort by soldToday if available
				result.sort((a, b) => (b.soldToday || 0) - (a.soldToday || 0));
				break;
		}

		return result;
	}, [filters, sortBy]);

	const handleFilterChange = (newFilters: Filters) => {
		setFilters(newFilters);
	};

	const activeFilterCount =
		filters.brands.length +
		filters.conditions.length +
		filters.storage.length +
		filters.features.length;

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-4">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-4">
					<a href="/" className="hover:text-primary-500 transition-colors">
						Home
					</a>
					<ChevronRight size={14} />
					<span className="text-gray-900 font-medium">All Products</span>
				</nav>

				{/* Page Header */}
				<div className="mb-4">
					<h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
						All Electronics
					</h1>
					<p className="text-gray-600 text-sm">
						{filteredAndSortedProducts.length} products available
					</p>
				</div>

				<div className="flex gap-6">
					{/* Filter Sidebar - Desktop */}
					<div className="hidden lg:block w-80 flex-shrink-0">
						<FilterSidebar
							onFilterChange={handleFilterChange}
							isOpen={true}
							onClose={() => {}}
						/>
					</div>

					{/* Main Content */}
					<div className="flex-1">
						{/* Toolbar */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-4">
							<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
								{/* Mobile Filter Button */}
								<button
									onClick={() => setIsFilterOpen(true)}
									className="lg:hidden flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-full font-medium hover:bg-primary-600 transition-colors shadow-md"
								>
									<SlidersHorizontal size={18} />
									Filters
									{activeFilterCount > 0 && (
										<span className="bg-white text-primary-500 text-xs px-2 py-0.5 rounded-full font-bold">
											{activeFilterCount}
										</span>
									)}
								</button>

								{/* Sort Dropdown */}
								<div className="flex items-center gap-3">
									<label className="text-sm font-medium text-gray-700 hidden sm:block">
										Sort by:
									</label>
									<select
										value={sortBy}
										onChange={(e) => setSortBy(e.target.value as SortOption)}
										className="flex-1 sm:flex-none px-4 py-2 border border-gray-300 rounded-xl text-sm font-medium text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-600"
									>
										{sortOptions.map((option) => (
											<option key={option.value} value={option.value}>
												{option.label}
											</option>
										))}
									</select>
								</div>

								{/* View Toggle - Desktop Only */}
								<div className="hidden sm:flex items-center gap-2 bg-gray-100 rounded-full p-1">
									<button
										onClick={() => setViewMode("grid")}
										className={`p-2 rounded-full transition-colors ${
											viewMode === "grid"
												? "bg-white text-primary-500 shadow-sm"
												: "text-gray-600 hover:text-gray-900"
										}`}
										aria-label="Grid view"
									>
										<Grid3x3 size={18} />
									</button>
									<button
										onClick={() => setViewMode("list")}
										className={`p-2 rounded-full transition-colors ${
											viewMode === "list"
												? "bg-white text-primary-500 shadow-sm"
												: "text-gray-600 hover:text-gray-900"
										}`}
										aria-label="List view"
									>
										<List size={18} />
									</button>
								</div>
							</div>

							{/* Active Filters Display */}
							{activeFilterCount > 0 && (
								<div className="mt-4 pt-4 border-t border-gray-200">
									<div className="flex flex-wrap gap-2">
										{filters.brands.map((brand) => (
											<span
												key={brand}
												className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
											>
												{brand}
											</span>
										))}
										{filters.conditions.map((condition) => (
											<span
												key={condition}
												className="px-3 py-1 bg-success-100 text-success-700 rounded-full text-sm font-medium"
											>
												{condition}
											</span>
										))}
										{filters.storage.map((storage) => (
											<span
												key={storage}
												className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm font-medium"
											>
												{storage}
											</span>
										))}
										{filters.features.map((feature) => (
											<span
												key={feature}
												className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium"
											>
												{feature}
											</span>
										))}
									</div>
								</div>
							)}
						</div>

						{/* Products Grid */}
						{filteredAndSortedProducts.length > 0 ? (
							<div
								className={
									viewMode === "grid"
										? "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-3"
										: "space-y-3"
								}
							>
								{filteredAndSortedProducts.map((product) => (
									<ProductCard
										key={product.id}
										{...product}
										isFlashDeal={!!product.originalPrice}
									/>
								))}
							</div>
						) : (
							<div className="bg-white rounded-2xl shadow-card p-12 text-center">
								<div className="max-w-md mx-auto">
									<div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
										<SlidersHorizontal size={48} className="text-gray-400" />
									</div>
									<h3 className="text-xl font-bold text-gray-900 mb-2">
										No products found
									</h3>
									<p className="text-gray-600 mb-6">
										Try adjusting your filters to see more results
									</p>
									<button
										onClick={() =>
											setFilters({
												priceRange: [0, 10000000],
												brands: [],
												conditions: [],
												storage: [],
												features: [],
											})
										}
										className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
									>
										Clear All Filters
									</button>
								</div>
							</div>
						)}

						{/* Pagination Placeholder */}
						{filteredAndSortedProducts.length > 0 && (
							<div className="mt-8 flex justify-center">
								<div className="bg-white rounded-2xl shadow-card px-6 py-3">
									<p className="text-sm text-gray-600">
										Showing {filteredAndSortedProducts.length} of{" "}
										{allProducts.length} products
									</p>
								</div>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* Mobile Filter Sidebar */}
			<FilterSidebar
				onFilterChange={handleFilterChange}
				isOpen={isFilterOpen}
				onClose={() => setIsFilterOpen(false)}
			/>
		</div>
	);
}
