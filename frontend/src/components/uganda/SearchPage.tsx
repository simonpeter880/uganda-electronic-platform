"use client";

import { useState, useMemo } from "react";
import { Search, SlidersHorizontal, X, ChevronRight } from "lucide-react";
import ProductCard from "@/components/uganda/ProductCard";
import FilterSidebar, { Filters } from "@/components/uganda/FilterSidebar";
import { mockFeaturedProducts, mockFlashDeals } from "@/lib/mock-data";

// Combine all products
const allProducts = [...mockFlashDeals, ...mockFeaturedProducts].map((product) => ({
	...product,
	installmentPrice: Math.round(product.price / 3),
}));

export default function SearchPage() {
	const [searchQuery, setSearchQuery] = useState("");
	const [filters, setFilters] = useState<Filters>({
		priceRange: [0, 10000000],
		brands: [],
		conditions: [],
		storage: [],
		features: [],
	});
	const [isFilterOpen, setIsFilterOpen] = useState(false);

	// Search and filter products
	const results = useMemo(() => {
		if (!searchQuery.trim()) return [];

		let filtered = allProducts;

		// Apply search query
		const query = searchQuery.toLowerCase();
		filtered = filtered.filter((p) =>
			p.name.toLowerCase().includes(query) ||
			(p.brand && p.brand.toLowerCase().includes(query))
		);

		// Apply price range filter
		filtered = filtered.filter(
			(p) => p.price >= filters.priceRange[0] && p.price <= filters.priceRange[1]
		);

		// Apply brand filter
		if (filters.brands.length > 0) {
			filtered = filtered.filter((p) => {
				const nameLower = p.name.toLowerCase();
				return filters.brands.some((brand) => nameLower.includes(brand.toLowerCase()));
			});
		}

		// Apply storage filter
		if (filters.storage.length > 0) {
			filtered = filtered.filter((p) => {
				const nameLower = p.name.toLowerCase();
				return filters.storage.some((storage) => nameLower.includes(storage.toLowerCase()));
			});
		}

		return filtered;
	}, [searchQuery, filters]);

	const handleFilterChange = (newFilters: Filters) => {
		setFilters(newFilters);
	};

	const clearSearch = () => {
		setSearchQuery("");
		setFilters({
			priceRange: [0, 10000000],
			brands: [],
			conditions: [],
			storage: [],
			features: [],
		});
	};

	const activeFilterCount =
		filters.brands.length +
		filters.conditions.length +
		filters.storage.length +
		filters.features.length;

	// Popular searches
	const popularSearches = [
		"iPhone 14",
		"Samsung Galaxy",
		"MacBook Pro",
		"Gaming Laptop",
		"Headphones",
		"Smart Watch",
	];

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-6">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-6">
					<a href="/" className="hover:text-primary-600 transition-colors">
						Home
					</a>
					<ChevronRight size={16} />
					<span className="text-gray-900 font-medium">Search</span>
				</nav>

				{/* Search Header */}
				<div className="mb-8">
					<h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
						Search Products
					</h1>

					{/* Search Bar */}
					<div className="relative max-w-3xl">
						<Search
							size={24}
							className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
						/>
						<input
							type="text"
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							placeholder="Search for products, brands, or categories..."
							className="w-full pl-14 pr-24 py-4 text-lg border-2 border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent"
							autoFocus
						/>
						{searchQuery && (
							<button
								onClick={clearSearch}
								className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors"
							>
								<X size={20} className="text-gray-600" />
							</button>
						)}
					</div>

					{/* Popular Searches */}
					{!searchQuery && (
						<div className="mt-6">
							<p className="text-sm text-gray-600 mb-3">Popular Searches:</p>
							<div className="flex flex-wrap gap-2">
								{popularSearches.map((term) => (
									<button
										key={term}
										onClick={() => setSearchQuery(term)}
										className="px-4 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:border-primary-600 hover:text-primary-600 transition-colors"
									>
										{term}
									</button>
								))}
							</div>
						</div>
					)}
				</div>

				{searchQuery && (
					<div className="flex gap-6">
						{/* Filter Sidebar - Desktop */}
						<div className="hidden lg:block w-80 flex-shrink-0">
							<FilterSidebar
								onFilterChange={handleFilterChange}
								isOpen={true}
								onClose={() => {}}
							/>
						</div>

						{/* Search Results */}
						<div className="flex-1">
							{/* Results Header */}
							<div className="bg-white rounded-2xl shadow-card p-4 mb-6">
								<div className="flex items-center justify-between">
									<div>
										<h2 className="text-xl font-bold text-gray-900">
											Search Results for "{searchQuery}"
										</h2>
										<p className="text-gray-600 text-sm mt-1">
											{results.length} products found
										</p>
									</div>

									{/* Mobile Filter Button */}
									<button
										onClick={() => setIsFilterOpen(true)}
										className="lg:hidden flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
									>
										<SlidersHorizontal size={20} />
										Filters
										{activeFilterCount > 0 && (
											<span className="bg-white text-primary-600 text-xs px-2 py-0.5 rounded-full font-bold">
												{activeFilterCount}
											</span>
										)}
									</button>
								</div>

								{/* Active Filters */}
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
											{filters.storage.map((storage) => (
												<span
													key={storage}
													className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm font-medium"
												>
													{storage}
												</span>
											))}
										</div>
									</div>
								)}
							</div>

							{/* Results Grid */}
							{results.length > 0 ? (
								<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
									{results.map((product) => (
										<ProductCard
											key={product.id}
											{...product}
											isFlashDeal={!!product.originalPrice}
										/>
									))}
								</div>
							) : (
								<div className="bg-white rounded-2xl shadow-card p-12 text-center">
									<div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
										<Search size={48} className="text-gray-400" />
									</div>
									<h3 className="text-xl font-bold text-gray-900 mb-2">
										No Results Found
									</h3>
									<p className="text-gray-600 mb-6">
										We could not find any products matching "{searchQuery}"
									</p>
									<div className="space-y-3">
										<p className="text-sm text-gray-700 font-medium">
											Suggestions:
										</p>
										<ul className="text-sm text-gray-600 space-y-1">
											<li>Check your spelling</li>
											<li>Try more general keywords</li>
											<li>Try different keywords</li>
										</ul>
										<button
											onClick={clearSearch}
											className="mt-6 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
										>
											Clear Search
										</button>
									</div>
								</div>
							)}
						</div>
					</div>
				)}

				{/* Mobile Filter Sidebar */}
				<FilterSidebar
					onFilterChange={handleFilterChange}
					isOpen={isFilterOpen}
					onClose={() => setIsFilterOpen(false)}
				/>
			</div>
		</div>
	);
}
