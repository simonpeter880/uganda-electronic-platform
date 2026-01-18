"use client";

import { useState, useEffect } from "react";
import { Star, ChevronLeft, ChevronRight, MapPin } from "lucide-react";
import Image from "next/image";

interface Review {
	id: string;
	author: string;
	location: string;
	rating: number;
	comment: string;
	product: string;
	avatar?: string;
	verified: boolean;
}

interface ReviewsCarouselProps {
	reviews: Review[];
}

export default function ReviewsCarousel({ reviews }: ReviewsCarouselProps) {
	const [currentIndex, setCurrentIndex] = useState(0);

	useEffect(() => {
		const timer = setInterval(() => {
			setCurrentIndex((prev) => (prev + 1) % reviews.length);
		}, 5000);

		return () => clearInterval(timer);
	}, [reviews.length]);

	const goToPrevious = () => {
		setCurrentIndex((prev) => (prev - 1 + reviews.length) % reviews.length);
	};

	const goToNext = () => {
		setCurrentIndex((prev) => (prev + 1) % reviews.length);
	};

	if (reviews.length === 0) return null;

	return (
		<section className="py-12">
			<div className="container mx-auto px-4">
				<div className="text-center mb-8">
					<h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
						What Our Customers Say
					</h2>
					<p className="text-gray-600">
						⭐ 4.9/5 from over 2,500+ happy customers across Uganda
					</p>
				</div>

				<div className="relative max-w-4xl mx-auto">
					{/* Reviews */}
					<div className="relative overflow-hidden rounded-3xl bg-white shadow-xl p-8 md:p-12">
						{reviews.map((review, index) => (
							<div
								key={review.id}
								className={`transition-opacity duration-500 ${
									index === currentIndex ? "opacity-100" : "opacity-0 absolute inset-0 pointer-events-none"
								}`}
							>
								{/* Stars */}
								<div className="flex justify-center gap-1 mb-4">
									{[...Array(5)].map((_, i) => (
										<Star
											key={i}
											size={28}
											className={i < review.rating ? "fill-success-500 text-success-500" : "text-gray-300"}
										/>
									))}
								</div>

								{/* Comment */}
								<blockquote className="text-xl md:text-2xl text-gray-900 text-center mb-6 font-medium leading-relaxed">
									"{review.comment}"
								</blockquote>

								{/* Product */}
								<p className="text-sm text-primary-600 text-center mb-4 font-semibold">
									Purchased: {review.product}
								</p>

								{/* Author */}
								<div className="flex items-center justify-center gap-3">
									<div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
										{review.avatar ? (
											<Image
												src={review.avatar}
												alt={review.author}
												width={48}
												height={48}
												className="rounded-full"
											/>
										) : (
											<span className="text-primary-600 font-bold text-lg">
												{review.author.charAt(0)}
											</span>
										)}
									</div>
									<div className="text-left">
										<p className="font-bold text-gray-900 flex items-center gap-2">
											{review.author}
											{review.verified && (
												<span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
													✓ Verified
												</span>
											)}
										</p>
										<p className="text-sm text-gray-600 flex items-center gap-1">
											<MapPin size={14} />
											{review.location}
										</p>
									</div>
								</div>
							</div>
						))}
					</div>

					{/* Navigation */}
					<button
						onClick={goToPrevious}
						className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
						aria-label="Previous review"
					>
						<ChevronLeft size={24} className="text-gray-900" />
					</button>
					<button
						onClick={goToNext}
						className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
						aria-label="Next review"
					>
						<ChevronRight size={24} className="text-gray-900" />
					</button>

					{/* Dots */}
					<div className="flex justify-center gap-2 mt-6">
						{reviews.map((_, index) => (
							<button
								key={index}
								onClick={() => setCurrentIndex(index)}
								className={`h-2 rounded-full transition-all ${
									index === currentIndex ? "w-8 bg-primary-600" : "w-2 bg-gray-300"
								}`}
								aria-label={`Go to review ${index + 1}`}
							/>
						))}
					</div>
				</div>
			</div>
		</section>
	);
}
