"use client";

import { useState, useMemo } from "react";
import { MapPin, Search, TruckIcon } from "lucide-react";

interface District {
	id: string;
	name: string;
	region: "Central" | "Eastern" | "Northern" | "Western";
	deliveryFee: number;
	estimatedDays: number;
}

interface DistrictSelectorProps {
	districts: District[];
	selectedDistrict: District | null;
	onSelect: (district: District) => void;
	className?: string;
}

export default function DistrictSelector({
	districts,
	selectedDistrict,
	onSelect,
	className = "",
}: DistrictSelectorProps) {
	const [isOpen, setIsOpen] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");

	// Group districts by region
	const groupedDistricts = useMemo(() => {
		const filtered = districts.filter((d) =>
			d.name.toLowerCase().includes(searchQuery.toLowerCase())
		);

		return {
			Central: filtered.filter((d) => d.region === "Central"),
			Eastern: filtered.filter((d) => d.region === "Eastern"),
			Northern: filtered.filter((d) => d.region === "Northern"),
			Western: filtered.filter((d) => d.region === "Western"),
		};
	}, [districts, searchQuery]);

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
		}).format(amount);
	};

	return (
		<div className={`relative ${className}`}>
			{/* Trigger Button */}
			<button
				onClick={() => setIsOpen(!isOpen)}
				className="flex items-center gap-2 px-4 py-2.5 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-500 transition-colors w-full md:w-auto"
			>
				<MapPin size={20} className="text-primary-600" />
				<div className="flex-1 text-left">
					<p className="text-xs text-gray-600">Deliver to</p>
					<p className="font-semibold text-gray-900">
						{selectedDistrict ? selectedDistrict.name : "Select District"}
					</p>
				</div>
				{selectedDistrict && (
					<div className="ml-2 text-right hidden md:block">
						<p className="text-xs text-gray-600">Delivery Fee</p>
						<p className="text-sm font-bold text-primary-600">
							{formatPrice(selectedDistrict.deliveryFee)}
						</p>
					</div>
				)}
				<svg
					className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M19 9l-7 7-7-7"
					/>
				</svg>
			</button>

			{/* Dropdown */}
			{isOpen && (
				<>
					{/* Backdrop */}
					<div
						className="fixed inset-0 bg-black/20 z-40"
						onClick={() => setIsOpen(false)}
					/>

					{/* Dropdown Content */}
					<div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 max-h-[500px] overflow-hidden flex flex-col md:w-[400px]">
						{/* Search */}
						<div className="p-4 border-b border-gray-100">
							<div className="relative">
								<Search
									size={18}
									className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
								/>
								<input
									type="text"
									placeholder="Search district..."
									value={searchQuery}
									onChange={(e) => setSearchQuery(e.target.value)}
									className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:border-primary-500"
								/>
							</div>
						</div>

						{/* Districts List */}
						<div className="flex-1 overflow-y-auto p-2">
							{Object.entries(groupedDistricts).map(([region, regionDistricts]) => {
								if (regionDistricts.length === 0) return null;

								return (
									<div key={region} className="mb-4">
										<h4 className="text-sm font-bold text-gray-900 px-3 py-2 bg-gray-50 rounded-lg">
											{region} Region
										</h4>
										<div className="mt-1">
											{regionDistricts.map((district) => (
												<button
													key={district.id}
													onClick={() => {
														onSelect(district);
														setIsOpen(false);
														setSearchQuery("");
													}}
													className={`w-full flex items-center justify-between px-3 py-2.5 hover:bg-primary-50 rounded-lg transition-colors ${
														selectedDistrict?.id === district.id
															? "bg-primary-100 border border-primary-300"
															: ""
													}`}
												>
													<div className="flex items-center gap-2">
														<MapPin
															size={16}
															className={
																selectedDistrict?.id === district.id
																	? "text-primary-600"
																	: "text-gray-400"
															}
														/>
														<span className="font-medium text-gray-900">
															{district.name}
														</span>
													</div>
													<div className="text-right">
														<p className="text-sm font-bold text-primary-600">
															{formatPrice(district.deliveryFee)}
														</p>
														<p className="text-xs text-gray-500">
															{district.estimatedDays} {district.estimatedDays === 1 ? "day" : "days"}
														</p>
													</div>
												</button>
											))}
										</div>
									</div>
								);
							})}

							{searchQuery &&
								Object.values(groupedDistricts).every((arr) => arr.length === 0) && (
									<div className="text-center py-8">
										<MapPin size={48} className="mx-auto text-gray-300 mb-2" />
										<p className="text-gray-500">No districts found</p>
									</div>
								)}
						</div>

						{/* Footer Info */}
						{selectedDistrict && (
							<div className="p-4 bg-primary-50 border-t border-primary-100">
								<div className="flex items-center gap-2 text-sm">
									<TruckIcon size={18} className="text-primary-600" />
									<span className="text-gray-700">
										<span className="font-semibold">Free delivery</span> for orders over{" "}
										<span className="font-bold">UGX 1,000,000</span>
									</span>
								</div>
							</div>
						)}
					</div>
				</>
			)}
		</div>
	);
}
